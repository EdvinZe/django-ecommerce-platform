// self.addEventListener("push", function (event) {
//     const data = event.data.json()
  
//     event.waitUntil(
//       self.registration.showNotification(data.title, {
//         body: data.body,
//         icon: "/static/img/braskiu_logo.png",
//         data: {
//           url: data.url
//         }
//       })
//     )
//   })
  
//   self.addEventListener("notificationclick", function (event) {
//     event.notification.close()
//     event.waitUntil(
//       clients.openWindow(event.notification.data.url)
//     )
//   })
self.addEventListener("push", function (event) {
  const data = event.data ? event.data.json() : {}

  event.waitUntil(
    self.registration.showNotification(data.title || "Notification", {
      body: data.body || "",
      icon: "/static/img/braskiu_logo.png",
      data: {
        url: data.url || "/"
      }
    })
  )
})


self.addEventListener("notificationclick", function (event) {
  event.notification.close()

  const url = event.notification.data?.url || "/"

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true })
      .then(clientList => {
        for (const client of clientList) {
          if (client.url === url && "focus" in client) {
            return client.focus()
          }
        }
        return clients.openWindow(url)
      })
  )
})