# csvconnect2nadamillas (c) 2023 Baltasar MIT License <baltasarq@gmail.com>


from datetime import datetime
import json
import csv
import argparse


ETQ_WORKOUTS = "workouts"
ETQ_ID = "_id"
ETQ_YEAR = "year"
ETQ_MONTH = "month"
ETQ_DAY = "day"
ETQ_DISTANCE = "distance"
ETQ_TIME = "seconds_used"
ETQ_IS_POOL = "pool"


TYPE = "Tipo de actividad"
DATE = "Fecha"
DISTANCE = "Distancia"
TIME = "Tiempo"


def parse_type(str_t: str):
    """Determines whether the type is ows or pool swimming.
    
        :param str_t: The type of the swimming.
        :return: true if it is pool swimming, false otherwise.
    """
    str_t = str_t.strip().lower()
    pool_words = [
        "pool", "piscina", "alberca"
    ]
    
    return len([pw for pw in pool_words if pw in pool_words]) > 0


def read_csv(fn: str):
    with open(fn, "rt") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            yield row


def rec_2_json(id: int, rec: dict):
    """
    [{
        "_id":945,
        "year":2023,
        "month":6,
        "day":20,
        "distance":5247,
        "seconds_used":6400,
        "pool":false
        }...]
    """
    date = parse_date(rec[DATE])
    
    return {
        ETQ_ID: id,
        ETQ_YEAR: date.year,
        ETQ_MONTH: date.month - 1,
        ETQ_DAY: date.day,
        ETQ_DISTANCE: parse_distance(rec[DISTANCE]),
        ETQ_TIME: parse_time(rec[TIME]),
        ETQ_IS_POOL: parse_type(rec[TYPE])
    }


def parse_distance(str_d: str):
    return int(str_d.replace(".", ""))
    

def parse_time(str_t: str):
    str_parts = str_t.split(":")
    
    # Chk
    if len(str_parts) < 3:
        raise ValueError("Incorrect time: " + str_t)
        
    # Parse seconds
    str_seconds = str_parts[2]
    pos_comma_in_seconds = str_seconds.index(",") if "," in str_seconds else -1
    if pos_comma_in_seconds >= 0:
        str_seconds = str_seconds[:pos_comma_in_seconds]
    
    # Calculate
    hours = int(str_parts[0])
    minutes = int(str_parts[1])
    seconds = int(str_seconds)
    return (hours * 3600) + (minutes*60) + seconds
    

def parse_date(str_d: str):
    # Get rid of the time part
    str_date = str_d.split(" ")
    
    if len(str_date) < 2:
        raise ValueError("expected <date> <time>, and not: " + str_d)

    # Parse date in ISO format
    str_date = str_date[0]
    str_date_parts = str_date.split("-")
    
    if len(str_date_parts) < 3:
        raise ValueError("expected <year>-<month>-<day>, and not: " + str_d)

    year = int(str_date_parts[0])
    month = int(str_date_parts[1])
    day = int(str_date_parts[2])
    return datetime(year, month, day)


def record2str(rec: dict):
    """Tipo de actividad,          Fecha,               Distancia, Tiempo
       Natación en piscina,        2023-11-21 09:15:22, 5.200,     01:42:26
       Natación en aguas abiertas, 2023-11-21 09:15:22, 5.200,     01:42:26
    """

    return (str(parse_date(rec[DATE]).date())
            + " " + ("pool" if parse_type(rec[TYPE]) else "ows")
            + ": " + str(parse_distance(rec[DISTANCE]))
            + " @ " + str(parse_time(rec[TIME])) + " s") 
    

if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
                    prog="csvconnect2nadamillas",
                    description="Converts Garmin connect's CSV to \
                                 the nadamillas JSON format.",
                    epilog="baltasarq@gmail.com")
    parser.add_argument("filename",
                        help="the input file")
    parser.add_argument("-i", "--start_id",
                        type=int,
                        help="the starting id number (default is 0)")
    args = vars(parser.parse_args())
                    
                    
    # Determine file input
    id = args["start_id"] if args["start_id"] else 0
    input_file = args["filename"]
    output_file = "actividades.json"
    workouts = []
    print(f"Converting: {input_file}, id #{id}")    
    
    # Convert CSV
    for record in read_csv(input_file):
        print(f"Writing record #{id}: {record2str(record)}") 
        workouts += [rec_2_json(id, record)]
        id += 1
    
    # Write JSON
    with open(output_file, "wt") as f_out:
        json.dump({ETQ_WORKOUTS: workouts}, f_out)
    print("Finished.")
