
import multiprocessing
import psutil
import os

from .header import workspace, input_dir, success, warning, info, Specs

from .extractor.audio_extractor import extraction_task
from .transcriber.audio_segmenter import segmentation_task
from .transcriber.audio_transcriber import transcription_task
from .compressor.text_compressor import compression_task
from .summarizer.summarizer import summarization_task

def setup_task(input_file):
    # Create the workspace
    info(f"- Processing: \"{input_file}\"")
    ws = workspace(input_file)
    return ws


def cleaning_task(ws):
    # Cleaning the workspace
    print(f"- Cleaning of {ws.source_file}")
    ws.cleanup()


def termination_task(ws):
    # Process completed
    success(f"- Process completed for \"{ws.source_file}\"")


def mutex_executer(lock, task_function, arg):
    # Acquire the lock to ensure exclusive access to the critical section
    lock.acquire()
    try:
        task_function(arg)
    finally:
        # Release the lock to allow other processes to access the critical section
        lock.release()
    return lock


def semaphore_executer(semaphore, task_function, arg):
    # Acquire the semaphore to ensure limited access to the critical section
    semaphore.acquire()
    try:
        task_function(arg)
    finally:
        # Release the semaphore to allow other processes to access the critical section
        semaphore.release()
    return semaphore
    

def process_file(args):
    input_file, lock, semaphore = args
    # Process instructions
    ws = setup_task(input_file)
    extraction_task(ws)
    segmentation_task(ws)
    semaphore = semaphore_executer(semaphore, transcription_task, ws)
    compression_task(ws)
    semaphore = semaphore_executer(semaphore, summarization_task, ws)
    cleaning_task(ws)
    return ws


def gui():
    # Inform the user about potentially resource intensive procedure
    warning(f"All files in the \"{input_dir}\" directory will be transcribed:")

    # Get all files located in the "input/" directory
    file_list = [f for f in os.listdir("input/") if not f.startswith('.')]
    print("\t- " + "\n\t- ".join(file_list))

    # Wait for user response
    input("\n-- Press enter to proceed --")

    # Return the file_list
    return file_list


if __name__ == "__main__":
    # Define environment fork limit
    # os.environ["OMP_NUM_THREADS"] = str(1)

    # User prompt and get the list of files
    file_list = gui()

    # Create a multiprocessing Manager
    manager = multiprocessing.Manager()

    # Create a shared lock using the Manager
    shared_lock = manager.Lock()
    shared_semaphore = manager.Semaphore(3)

    # Create a multiprocessing pool with the desired number of workers
    pool = multiprocessing.Pool(processes=Specs.NUM_LOGICAL_CPU)

    # Process the files in parallel 
    ws_list = pool.map(process_file, [(file, shared_lock, shared_semaphore) for file in file_list])

    # Sequential Processing left to do
    for ws in ws_list:
        termination_task(ws)

    # Wait for all tasks to complete
    pool.close()
    pool.join()













