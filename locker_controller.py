"""Hardware adapter boundary. This project intentionally does not guess partner API endpoints."""
class SimulatedLockerController:
    mode = 'SIMULATED'
    def health(self): return {'ok': True, 'mode': self.mode, 'message': 'No physical hardware is connected.'}
    def unlock(self, hub_code: str, locker_code: str, authorization: str):
        return {'ok': False, 'mode': self.mode, 'message': 'Simulated only: physical unlock is not available.'}

# Replace/extend only after receiving the partner group's official API documentation.
locker_controller = SimulatedLockerController()
