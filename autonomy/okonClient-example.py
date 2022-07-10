import time
from okonClient import OkonClient, PacketType, PacketFlag

def handle_simulation_reset(args = None) -> None:
    print('sim resetted')

def handle_ping(args = None) -> None:
    print(f'RTT is {round((time.time() - float(args))*1000)}')

oc = OkonClient(ip="127.0.0.1", port=44210, sync_interval=.05, debug=False) #ping simRST hitNGZ hitFZ packet error
oc.on_event('simRST', handle_simulation_reset)
oc.on_event('ping', handle_ping)
okon = oc.okon
sim = oc.simulation
oc.connect()


sim.reset()
okon.disarm_motors()
okon.set_stable_vel(x=0,y=0,z=0)

oc.send(PacketType.PING, PacketFlag.NONE, str(time.time()))
time.sleep(.5)


print('setting pos')
okon.set_depth(.6)
print(okon.sens['baro']/1000/9.81+.3)
okon.set_stable_rot(y=okon.sens['imu']['rot']['y'])
print(okon.sens['imu']['rot']['y'])
okon.arm_motors()
time.sleep(1)

okon.set_stable_rot(y=50, add=True)
print('waiting')
while not okon.reachedTargetRotation(1):
    pass
time.sleep(.1)
print('done waiting')

okon.set_stable_rot(y=-50, add=True)
time.sleep(1)
okon.set_stable_vel(z=1)
while len(okon.get_detection('gate')) > 0:
    pass
time.sleep(1)
okon.set_stable_vel(z=0)