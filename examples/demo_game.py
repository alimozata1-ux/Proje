"""Demo: Pixel tarzı mini şehir sahnesi."""

from pixel_engine import PixelEngine, create_car, create_city_map, create_enemy_drone, create_tree, create_wall


def build_scene(engine: PixelEngine) -> None:
    game_map = create_city_map(width_tiles=80, height_tiles=45, tile_size=16)
    engine.set_map(game_map)

    engine.add_object(create_car(64, 64))
    engine.add_object(create_enemy_drone(200, 120, speed=75))
    engine.add_object(create_enemy_drone(400, 250, speed=120))

    # Statik nesneler
    engine.add_object(create_wall(280, 180, 90, 26))
    engine.add_object(create_wall(520, 310, 120, 20))
    engine.add_object(create_tree(180, 320))
    engine.add_object(create_tree(620, 220))


if __name__ == "__main__":
    app = PixelEngine(width=960, height=540, title="Pixel2D Demo", fps=60)
    app.run(on_start=build_scene)
