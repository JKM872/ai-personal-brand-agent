/**
 * Lightweight Zero-Dependency Website Tracker (0,00 PLN).
 * Drop this script into your website: <script src="/tracker.js"></script>
 * Automatically records UTM clicks and newsletter leads to your Supabase backend.
 */
(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const utmCampaign = urlParams.get('utm_campaign') || urlParams.get('ref');
  const utmSource = urlParams.get('utm_source') || 'direct';

  // 1. Zapis kliknięcia w pamięci sesji (żeby nie naliczać wielokrotnie przy odświeżaniu)
  if (utmCampaign && !sessionStorage.getItem('tracked_' + utmCampaign)) {
    sessionStorage.setItem('tracked_' + utmCampaign, 'true');
    console.log('[AI Tracker] Wykryto wejście z kampanii agenta:', utmCampaign);
    
    // Opcjonalnie: wyślij ping do API Twojej bazy Supabase lub własnego endpointu
    const supabaseUrl = window.SUPABASE_URL;
    const supabaseAnonKey = window.SUPABASE_ANON_KEY;
    if (supabaseUrl && supabaseAnonKey) {
      fetch(`${supabaseUrl}/rest/v1/rpc/increment_click`, {
        method: 'POST',
        headers: {
          'apikey': supabaseAnonKey,
          'Authorization': 'Bearer ' + supabaseAnonKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tag: utmCampaign })
      }).catch(() => {});
    }
  }

  // 2. Globalna funkcja do zapisu leada do newslettera
  window.subscribeToNewsletter = function(email, callback) {
    const supabaseUrl = window.SUPABASE_URL;
    const supabaseAnonKey = window.SUPABASE_ANON_KEY;
    if (!email || !supabaseUrl || !supabaseAnonKey) {
      if (callback) callback(false, "Brak konfiguracji lub adresu email");
      return;
    }
    fetch(`${supabaseUrl}/rest/v1/subscribers`, {
      method: 'POST',
      headers: {
        'apikey': supabaseAnonKey,
        'Authorization': 'Bearer ' + supabaseAnonKey,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ email: email, source_utm: utmCampaign || 'organic' })
    }).then(res => {
      if (res.ok && callback) callback(true, "Zapisano pomyślnie!");
      else if (callback) callback(false, "Błąd zapisu");
    }).catch(err => {
      if (callback) callback(false, err.message);
    });
  };
})();
