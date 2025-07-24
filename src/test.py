from display.fonts.font16x16 import font


def print_character(char):
    for column in range(16):
        ascii_no = ord(char)
        character_index = (ascii_no - 32) * 16
        char_data = font[character_index + column]
        row_chars = ""
        for row in range(16):
            pixel = char_data >> row
            if pixel & 1:
                row_chars = row_chars + "X"
            else:
                row_chars = row_chars + " "
        print(f"{row_chars}\n")


def main():
    print_character('"')


main()
