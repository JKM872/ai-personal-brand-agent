"""
Website CMS Article Publisher with Strict Owner Permission Gate.
Allows the AI Agent to publish SEO/GEO articles directly to the owner's website
ONLY when the owner explicitly grants permission (owner_authorized = True).

Supported Website Backends:
1. Git-based CMS (Next.js, Astro, Remix, Hugo, Jekyll via GitHub API)
2. WordPress REST API (/wp-json/wp/v2/posts)
3. Custom REST / Webhook Endpoint (POST with Bearer Token)
"""

import os
import json
import base64
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
PROFILE_PATH = BASE_DIR / "saas_core" / "product_profile.json"

def load_cms_permissions() -> dict:
    if PROFILE_PATH.exists():
        try:
            data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
            perms = data.get("cms_permissions", {})
            if perms:
                return perms
        except Exception:
            pass

    # Fallback default permissions (Safe: requires owner approval by default)
    return {
        "owner_authorized": os.environ.get("CMS_OWNER_AUTHORIZED", "false").lower() == "true",
        "publish_mode": os.environ.get("CMS_PUBLISH_MODE", "require_approval"), # 'require_approval' or 'autonomous'
        "cms_type": os.environ.get("CMS_TYPE", "github_markdown"), # 'github_markdown', 'wordpress', 'custom_webhook'
        "webhook_url": os.environ.get("CMS_WEBHOOK_URL", ""),
        "cms_api_key": os.environ.get("CMS_API_KEY", ""),
        "wp_url": os.environ.get("WP_SITE_URL", ""),
        "wp_user": os.environ.get("WP_USERNAME", ""),
        "wp_app_password": os.environ.get("WP_APP_PASSWORD", ""),
        "gh_repo": os.environ.get("CMS_GH_REPO", ""),
        "gh_token": os.environ.get("CMS_GH_TOKEN", ""),
        "gh_path_prefix": os.environ.get("CMS_GH_PATH", "content/blog")
    }

def build_frontmatter_markdown(article: dict, profile: dict) -> str:
    """Adds standard YAML Frontmatter for Next.js / Astro / MDX blogs."""
    now_iso = datetime.now().strftime("%Y-%m-%d")
    title = article.get("title", "").replace('"', '\\"')
    slug = article.get("slug", "")
    cat = profile.get("category", "Technologia & Biznes")
    frontmatter = f"""---
title: "{title}"
slug: "{slug}"
date: "{now_iso}"
category: "{cat}"
author: "{profile.get('product_name', 'Redakcja AI')}"
draft: false
---

"""
    return frontmatter + article.get("markdown", "")

def publish_article_to_website(article: dict, profile: dict, force_owner_override: bool = False) -> dict:
    """
    Publishes an article to the connected website ONLY if owner permissions allow it.
    """
    perms = load_cms_permissions()
    is_authorized = perms.get("owner_authorized", False) or force_owner_override
    publish_mode = perms.get("publish_mode", "require_approval")
    cms_type = perms.get("cms_type", "github_markdown")

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "slug": article.get("slug"),
        "title": article.get("title"),
        "owner_authorized": is_authorized,
        "publish_mode": publish_mode,
        "cms_type": cms_type,
        "status": "AWAITING_OWNER_PERMISSION"
    }

    # Gate 1: Check if owner granted permission
    if not is_authorized:
        result["message"] = "Wstrzymano publikację: Właściciel nie nadał jeszcze uprawnień zapisu na stronie (owner_authorized = false). Artykuł czeka jako bezpieczny szkic."
        return result

    # Gate 2: Check if mode requires manual 1-click approval per article
    if publish_mode == "require_approval" and not force_owner_override:
        result["status"] = "PENDING_1CLICK_APPROVAL"
        result["message"] = "Uprawnienia nadane w trybie 'require_approval' — artykuł oczekuje na 1 kliknięcie zatwierdzające w panelu właściciela."
        return result

    # Gate 3: Owner authorized autonomous publishing -> Execute dispatch!
    full_mdx = build_frontmatter_markdown(article, profile)

    # 1. Custom Webhook CMS (Next.js / Custom Backend / Ghost / Make)
    if cms_type == "custom_webhook" and perms.get("webhook_url"):
        try:
            payload = {
                "title": article.get("title"),
                "slug": article.get("slug"),
                "markdown": full_mdx,
                "raw_markdown": article.get("markdown"),
                "schema_json_ld": article.get("schema_json"),
                "published_at": datetime.now().isoformat()
            }
            headers = {"Content-Type": "application/json"}
            if perms.get("cms_api_key"):
                headers["Authorization"] = f"Bearer {perms['cms_api_key']}"
            req = urllib.request.Request(
                perms["webhook_url"],
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result["status"] = f"PUBLISHED_LIVE (Webhook HTTP {resp.status})"
                result["message"] = "Artykuł opublikowany automatycznie na stronie właściciela."
                return result
        except Exception as e:
            result["status"] = f"CMS_ERROR: {e}"
            return result

    # 2. WordPress REST API
    if cms_type == "wordpress" and perms.get("wp_url") and perms.get("wp_user") and perms.get("wp_app_password"):
        try:
            wp_endpoint = perms["wp_url"].rstrip("/") + "/wp-json/wp/v2/posts"
            creds = base64.b64encode(f"{perms['wp_user']}:{perms['wp_app_password']}".encode("utf-8")).decode("utf-8")
            payload = {
                "title": article.get("title"),
                "slug": article.get("slug"),
                "content": article.get("markdown"),
                "status": "publish"
            }
            req = urllib.request.Request(
                wp_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result["status"] = f"PUBLISHED_WORDPRESS (HTTP {resp.status})"
                result["message"] = "Artykuł opublikowany na WordPressie właściciela."
                return result
        except Exception as e:
            result["status"] = f"WP_ERROR: {e}"
            return result

    # 3. GitHub Markdown CMS (Astro / Next.js / Cloudflare Pages)
    if cms_type == "github_markdown" and perms.get("gh_repo") and perms.get("gh_token"):
        try:
            prefix = perms.get("gh_path_prefix", "content/blog").strip("/")
            file_path = f"{prefix}/{article.get('slug')}.md"
            api_url = f"https://api.github.com/repos/{perms['gh_repo']}/contents/{file_path}"
            encoded_content = base64.b64encode(full_mdx.encode("utf-8")).decode("utf-8")
            payload = {
                "message": f"📝 Auto-publish SEO article: {article.get('title')}",
                "content": encoded_content
            }
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {perms['gh_token']}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "PolsiaZeroAgent/2.0"
                },
                method="PUT"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result["status"] = f"PUBLISHED_GITHUB_CMS (HTTP {resp.status})"
                result["message"] = f"Artykuł wdrożony bezpośrednio do repozytorium strony ({perms['gh_repo']}/{file_path})."
                return result
        except Exception as e:
            result["status"] = f"GH_CMS_ERROR: {e}"
            return result

    # Default local public/articles deployment (already hosted on Cloudflare Pages!)
    result["status"] = "PUBLISHED_LOCAL_CLOUDFLARE_CMS"
    result["message"] = f"Właściciel nadał uprawnienia: artykuł opublikowany w public/articles/{article.get('slug')}.md z pełnym Frontmatterem MDX."
    mdx_path = BASE_DIR / "public" / "articles" / f"{article.get('slug')}.md"
    mdx_path.parent.mkdir(parents=True, exist_ok=True)
    mdx_path.write_text(full_mdx, encoding="utf-8")
    return result
