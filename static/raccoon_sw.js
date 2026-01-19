self.addEventListener('push', function (event) {
    if (!(self.Notification && self.Notification.permission === 'granted')) {
        return;
    }

    const data = event.data ? event.data.json() : {};
    const title = data.title || "アライグマからのお知らせ";
    const message = data.body || "お片付けの時間だよ！";
    const icon = "/static/raccoon_icon.png"; // Placeholder

    const options = {
        body: message,
        icon: icon,
        badge: icon
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/static/raccoon.html')
    );
});
