from poslog import PosLogCRF

import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m poslog 'input log message'")
        sys.exit(1)

    msg = sys.argv[1]
    pos_log= PosLogCRF()
    result = pos_log.predict_string_as_tuple(msg)
    print(result)

if __name__ == "__main__":
    main()