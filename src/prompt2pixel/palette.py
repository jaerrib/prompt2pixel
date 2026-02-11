class PaletteLoader:
    @staticmethod
    def load_gpl_palette(path: str) -> list[tuple[int, int, int]]:
        palette = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line[0].isdigit():
                    parts = line.split()
                    r, g, b = map(int, parts[:3])
                    palette.append((r, g, b))
        return palette

    @staticmethod
    def nearest_color(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]):
        r, g, b = rgb
        best = None
        best_dist = float("inf")
        for pr, pg, pb in palette:
            dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist < best_dist:
                best_dist = dist
                best = (pr, pg, pb)
        return best
