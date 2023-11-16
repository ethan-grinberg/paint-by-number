from src.pbn_gen import PbnGen


def main():
    images = ["panda", "landscape", "flower", "portrait"]
    dir = "frontend/src/assets/"
    for image in images:
        f_name = dir + image
        pbn = PbnGen(f_name + ".jpg")
        pbn.set_final_pbn()
        palette = pbn.output_to_svg(f_name + ".svg", f_name + ".json")


if __name__ == "__main__":
    main()
