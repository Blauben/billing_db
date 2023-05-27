from controller import initDatabase, initFileStructure
import console


def main():
    initDatabase()
    initFileStructure()
    console.run()


if __name__ == "__main__":
    main()
