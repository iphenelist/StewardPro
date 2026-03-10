const CACHE_NAME = "stewardpro-shell-{{ build_version }}";
const OFFLINE_URL = "/stewardpro-offline";
const CORE_ASSETS = [
	OFFLINE_URL,
	"/stewardpro-manifest.json",
	"/assets/stewardpro/pwa/icons/stewardpro-icon-192.png",
	"/assets/stewardpro/pwa/icons/stewardpro-icon-512.png",
	"/assets/stewardpro/pwa/icons/apple-touch-icon.png",
	"/assets/stewardpro/pwa/icons/stewardpro-icon.svg",
];

self.addEventListener("install", (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
	);
});

self.addEventListener("activate", (event) => {
	event.waitUntil(
		caches
			.keys()
			.then((keys) =>
				Promise.all(keys.filter((key) => key.startsWith("stewardpro-shell-") && key !== CACHE_NAME).map((key) => caches.delete(key)))
			)
			.then(() => self.clients.claim())
	);
});

self.addEventListener("fetch", (event) => {
	const { request } = event;
	if (request.method !== "GET") {
		return;
	}

	const url = new URL(request.url);
	if (url.origin !== self.location.origin) {
		return;
	}

	if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/socket.io")) {
		return;
	}

	if (request.mode === "navigate") {
		event.respondWith(
			fetch(request).catch(async () => {
				const cache = await caches.open(CACHE_NAME);
				return cache.match(OFFLINE_URL);
			})
		);
		return;
	}

	if (url.pathname.startsWith("/assets/") || url.pathname === "/stewardpro-manifest.json") {
		event.respondWith(
			caches.match(request).then((cachedResponse) => {
				const networkResponse = fetch(request)
					.then(async (response) => {
						if (response.ok) {
							const cache = await caches.open(CACHE_NAME);
							cache.put(request, response.clone());
						}
						return response;
					})
					.catch(() => cachedResponse);

				return cachedResponse || networkResponse;
			})
		);
	}
});
