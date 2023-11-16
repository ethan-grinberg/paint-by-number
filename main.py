from src.pbn_gen import PbnGen


def main():
    pbn = PbnGen("images/red_panda.jpg")
    pbn.set_final_pbn()
    palette = pbn.output_to_svg("path.svg")


if __name__ == "__main__":
    main()
