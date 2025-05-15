self.addEventListener('install', function (e) {
    console.log('Service Worker instalado');
});

self.addEventListener('fetch', function (e) {
    // Permite navegação offline básica (ajustável depois)
});
