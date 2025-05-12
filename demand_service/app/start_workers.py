import threading
from task_workers import (
    validate_demand_worker,
    check_object_availability_worker,
    check_user_balance_worker,
    update_ownership_worker
)

def main():
    # Create threads for each worker
    workers = [
        threading.Thread(target=validate_demand_worker),
        threading.Thread(target=check_object_availability_worker),
        threading.Thread(target=check_user_balance_worker),
        threading.Thread(target=update_ownership_worker)
    ]

    # Start all workers
    for worker in workers:
        worker.daemon = True
        worker.start()

    # Wait for all workers to finish (which they won't since they run indefinitely)
    for worker in workers:
        worker.join()

if __name__ == '__main__':
    main() 