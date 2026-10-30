import re, pathlib
W = pathlib.Path("agents/writers")
names = ["ads", "community", "github", "linkedin", "newsletter", "outreach", "twitter", "video"]
for n in names:
    p = W / f"{n}_writer.py"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"def (generate_\w+)\(topic, persona(, secondaries=None)?\):",
               lambda m: f"def {m.group(1)}(topic, persona{m.group(2) or ''}, project=None, brand=None):", s, count=1)
    s = s.replace("    profile = load_product_profile()", "    profile = resolve_profile(project)", 1)
    s = s.replace("derive_seo_headline(profile, topic)", "headline(profile, topic)")
    # brand voice into AI system prompts: ask_free_ai(<first arg string>, ...
    s = re.sub(r'ask_free_ai\(\n(\s+)(f?"[^"\n]*")(,)', lambda m: f'ask_free_ai(\n{m.group(1)}{m.group(2)} + brand_prompt(brand){m.group(3)}', s)
    # import
    s = re.sub(r"^from agents\.geo_seo_engine import [^\n]+\n",
               "from agents.writers._common import resolve_profile, headline, brand_prompt\n", s, count=1, flags=re.M)
    if "from agents.writers._common" not in s:
        s = s.replace("\nimport json\n", "\nimport json\nfrom agents.writers._common import resolve_profile, headline, brand_prompt\n", 1)
    p.write_text(s, encoding="utf-8", newline="")
    print(n, "brand_prompt" in s.split("import")[-1], "resolve_profile(project)" in s)
