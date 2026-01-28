import cv2
import numpy as np


class AntiSpoofDetector:
    """
    Practical anti-spoofing detector for webcam-based systems.
    Uses relaxed heuristics + score-based voting to avoid false positives.
    """

    def __init__(self):
        # Tuned for real webcam conditions
        self.blur_min = 20          # Too low = printed photo / flat image
        self.color_min = 8          # Skin tone variation threshold
        self.texture_min = 0.08     # Natural facial texture threshold

    def is_real_face(self, image):
        """
        Main spoof detection function.
        Returns True if face is likely real.
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            blur_score = self._calculate_blur(gray)
            color_score = self._calculate_color_diversity(image)
            texture_score = self._analyze_texture(gray)

            # Score-based voting (2 out of 3 must pass)
            score = 0

            if blur_score > self.blur_min:
                score += 1
            if color_score > self.color_min:
                score += 1
            if texture_score > self.texture_min:
                score += 1

            return score >= 2

        except Exception as e:
            print(f"[AntiSpoof ERROR] {e}")
            # Fail-open for better UX
            return True

    def _calculate_blur(self, gray_image):
        """
        Laplacian variance for blur detection.
        """
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return laplacian.var()

    def _calculate_color_diversity(self, image):
        """
        Measures color variation.
        Screens & printed photos usually have low variance.
        """
        if len(image.shape) != 3:
            return 0

        std_r = np.std(image[:, :, 0])
        std_g = np.std(image[:, :, 1])
        std_b = np.std(image[:, :, 2])

        return (std_r + std_g + std_b) / 3

    def _analyze_texture(self, gray_image):
        """
        Texture analysis using gradient magnitude.
        """
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

        gradient_magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)

        return np.mean(gradient_magnitude) / 255.0

    def get_spoof_confidence(self, image):
        """
        Optional confidence-based spoof detection.
        Returns (is_real, confidence_score)
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            blur = min(self._calculate_blur(gray) / 2000, 1.0)
            color = min(self._calculate_color_diversity(image) / 50, 1.0)
            texture = min(self._analyze_texture(gray) / 0.3, 1.0)

            confidence = (blur * 0.4) + (color * 0.3) + (texture * 0.3)

            return confidence > 0.5, confidence

        except Exception as e:
            print(f"[AntiSpoof Confidence ERROR] {e}")
            return True, 0.5
