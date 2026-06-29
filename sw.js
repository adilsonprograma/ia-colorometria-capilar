const CACHE_NAME = 'coloria-v3';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './style.css',
  './index.js',
  './manifest.json'
];

// Instalação do Service Worker (Salva os arquivos em Cache)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Fazendo cache dos arquivos offline...');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// Ativação e Limpeza de Caches antigos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('[Service Worker] Removendo cache antigo', key);
          return caches.delete(key);
        }
      }));
    })
  );
});

// Interceptando requisições: se estiver sem internet, puxa do Cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Se encontrou no cache, retorna ele instantaneamente
      return cachedResponse || fetch(event.request);
    })
  );
});
