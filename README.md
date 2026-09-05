# Upscale Program

Kişisel videoları GPU olmadan (Intel Iris Xe entegre grafik üzerinden Vulkan
ile) yükseltmek için basit bir araç. Örnek: 360p -> 1080p.

## Nasıl çalışır

1. `ffmpeg` video karelerini çıkarır.
2. `realesrgan-ncnn-vulkan.exe` her kareyi yükseltir (Vulkan ile Iris Xe kullanır).
3. `ffmpeg` yükseltilmiş kareleri tekrar videoya dönüştürür ve orijinal sesi ekler.

## Kurulum

Gerekli: Python 3.12+, `ffmpeg`/`ffprobe` PATH'te olmalı (zaten kurulu).

```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_engine.ps1
```

Bu script Real-ESRGAN motorunu (yaklaşık 45MB, xinntao/Real-ESRGAN GitHub
releases) indirir ve `tools/realesrgan-ncnn-vulkan/` klasörüne kurar.

## Kullanım

GUI:

```bash
python main.py
```

Komut satırı:

```bash
python upscale.py girdi.mp4 cikti.mp4 --model realesr-animevideov3 --scale 3
```

## Modeller

| Model | Ölçek | Kullanım |
|---|---|---|
| `realesr-animevideov3` | 2, 3, 4 | Gerçek video, hızlı, varsayılan |
| `realesrgan-x4plus` | 4 | Genel fotoğraf/video, daha kaliteli, yavaş |
| `realesrgan-x4plus-anime` | 4 | Çizgi film/anime içerik |

360p -> 1080p için `realesr-animevideov3` model + ölçek 3 doğrudan uygun.

## Donanım notu

GPU yok, Intel i9-13900H + Iris Xe. Vulkan hızlandırma kullanılıyor ama yine
de CPU/GPU işlemci yükü yüksek olur, laptop ısınabilir. Uzun videolarda kısa
parçalar halinde test etmek önerilir.
