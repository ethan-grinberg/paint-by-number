from src.pbn_gen import PbnGen
import sys
import os


def main():
    if not len(sys.argv) == 2:
        print("Error: No input image provided")
        exit(1)

    input_image = sys.argv[1]
    dir_name = os.path.dirname(input_image)
    try:
        pbn = PbnGen(input_image)
        pbn.set_final_pbn()
        pbn.output_to_svg(
            os.path.join(dir_name, "pbn.svg"), os.path.join(dir_name, "pbn.json")
        )
    except Exception as e:
        print("error generating PBN - make sure the image exists")
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
