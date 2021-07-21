import mmap
import time
import struct


MUMBLE_LINK_SIZE = 5460
PAGE_SIZE = 4096
OUTFILE = "Z:\\tmp\\gw2_mumble_link"
ACTIVE_SLEEP_TIME = 1/30 # 30 updates per second
INACTIVE_SLEEP_TIME = 5 # 1 update every 5 seconds

TICKS_PER_SECOND = 1/ACTIVE_SLEEP_TIME
SECONDS_UNTIL_INACTIVE = 10
TICKS_UNTIL_INACTIVE = round(TICKS_PER_SECOND * SECONDS_UNTIL_INACTIVE)


def main():
    with mmap.mmap(fileno=-1, length=MUMBLE_LINK_SIZE, tagname="MumbleLink") as in_file:
        with open(OUTFILE, "wb") as out_file:
            previous_tick = None
            missed_ticks = 0
            while True:
                # Seek both input and output to the beginning
                in_file.seek(0)
                out_file.seek(0)

                # Read the raw bytes
                data = in_file.read(PAGE_SIZE)

                # Unpack tick number
                tick = struct.unpack_from("I", data, offset=4)[0]

                # If the tick didn't change, this is a missed tick
                if tick == 0 or tick == previous_tick:
                    #print("Missed Tick: {}/{} ({})".format(missed_ticks, TICKS_UNTIL_INACTIVE, tick)) # Debug missed tick number
                    missed_ticks += 1
                else:
                    #print("Good Tick:", tick) # Debug tick number
                    #print(data[:32].hex()) # Debug preview of data
                    missed_ticks = 0
                    out_file.write(data)
                
                previous_tick = tick

                # If too many ticks are missed, go into inactive mode
                if missed_ticks > TICKS_UNTIL_INACTIVE:
                    time.sleep(INACTIVE_SLEEP_TIME)
                else:
                    time.sleep(ACTIVE_SLEEP_TIME)


if __name__ == "__main__":
    main()