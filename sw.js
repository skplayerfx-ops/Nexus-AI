const CACHE_NAME = 'nexus-ai-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/image_3.png',
  '/image_4.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
