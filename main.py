from src.pbn_gen import PbnGen


def main():
    pbn = PbnGen("images/red_panda.jpg")
    pbn.set_final_pbn()
    palette = pbn.output_to_svg(
        "frontend/src/assets/panda.svg", "frontend/src/assets/panda.json"
    )


if __name__ == "__main__":
    main()
