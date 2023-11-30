from src.pbn_gen import PbnGen


def main():
    images = ["panda", "landscape", "flower", "portrait"]
    dir = "frontend/public/"
    out_dir = "frontend/src/assets/"
    for image in images:
        f_name = dir + image
        out_name = out_dir + image
        pbn = PbnGen(f_name + ".jpg")
        pbn.set_final_pbn()
        palette = pbn.output_to_svg(out_name + ".svg", out_name + ".json")


if __name__ == "__main__":
    main()
