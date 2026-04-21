document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("subscribe-btn");
  const unsubscribeBtn = document.getElementById("unsubscribe-btn");

  function getCSRFToken() {
    return document.cookie
      .split("; ")
      .find(row => row.startsWith("csrftoken"))
      ?.split("=")[1];
  }

  function urlBase64ToUint8Array(base64String) {
    if (!base64String) {
      console.error("❌ VAPID key is missing");
      return null;
    }

    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, "+")
      .replace(/_/g, "/");

    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
  }

  // 👉 SUBSCRIBE
  if (btn) {
    btn.addEventListener("click", async () => {
      try {
        if (!("serviceWorker" in navigator)) {
          alert("❌ Naršyklė nepalaiko pranešimų");
          return;
        }

        if (!window.VAPID_PUBLIC_KEY) {
          alert("❌ Nėra VAPID rakto");
          return;
        }

        const registration = await navigator.serviceWorker.register("/static/js/sw.js");

        const permission = await Notification.requestPermission();

        if (permission !== "granted") {
          alert("❌ Leiskite pranešimus");
          return;
        }

        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY)
        });

        await fetch("/api/push/subscribe/", {
          method: "POST",
          body: JSON.stringify(subscription),
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
          }
        });

        window.location.reload();

      } catch (err) {
        console.error("Push error:", err);
        alert("❌ Klaida su pranešimais");
      }
    });
  }

  // 👉 UNSUBSCRIBE
  if (unsubscribeBtn) {
    unsubscribeBtn.addEventListener("click", async () => {
      try {
        const registration = await navigator.serviceWorker.register("/static/js/sw.js");

        const subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
          alert("❌ Jūs nesate prenumeravę");
          return;
        }

        await fetch("/api/push/unsubscribe/", {
          method: "POST",
          body: JSON.stringify(subscription),
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
          }
        });

        await subscription.unsubscribe();

        window.location.reload();

      } catch (err) {
        console.error("Unsubscribe error:", err);
        alert("❌ Klaida atsisakant prenumeratos");
      }
    });
  }
});