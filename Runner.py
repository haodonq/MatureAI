try:
    from malmo import MalmoPython
except:
    import MalmoPython
    import malmoutils

import os
import sys
import time
import json

def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    print("Starting Mission {}.".format(role))
    max_retries = 5
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expId)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2)

def safeWaitForStart(agent_hosts):
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow a two minute timeout.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            exit(1)
        time.sleep(0.1)
        print(".", end=' ')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start.")
        exit(1)
    print()
    print("Mission has started.")

def GetXML():
    TNT_and_TRIGGERS = ""
    Fence = f"<DrawBlock x='0' y='50' z='-42' type='jungle_fence_gate'/> \n"
    # Fence += f"<DrawBlock x='1' y='50' z='-40' type='jungle_fence_gate'/> \n"
    # Fence += f"<DrawBlock x='-1' y='50' z='-40' type='jungle_fence_gate'/> \n"
    # Fence += f"<DrawBlock x='2' y='50' z='-40' type='jungle_fence_gate'/> \n"

    trigger_z = [i for i in range(-48, 50, 7)]

    for i in trigger_z:
        TNT_and_TRIGGERS += f"<DrawBlock x='-1' y='48' z='{i}' type='tnt'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='-0' y='48' z='{i}' type='tnt'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='1' y='48' z='{i}' type='tnt'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='2' y='48' z='{i}' type='tnt'/> \n"

        TNT_and_TRIGGERS += f"<DrawBlock x='-1' y='50' z='{i}' type='light_weighted_pressure_plate'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='-0' y='50' z='{i}' type='light_weighted_pressure_plate'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='1' y='50' z='{i}' type='light_weighted_pressure_plate'/> \n"
        TNT_and_TRIGGERS += f"<DrawBlock x='2' y='50' z='{i}' type='light_weighted_pressure_plate'/> \n"

    with open("xml.txt", "w") as f:
        f.write(TNT_and_TRIGGERS)

    missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        
                        <About>
                            <Summary>Runner</Summary>
                        </About>
        
                        <ServerSection>
                            <ServerInitialConditions>
                                <Time>
                                    <StartTime>0</StartTime>
                                    <AllowPassageOfTime>false</AllowPassageOfTime>
                                </Time>
                                <Weather>clear</Weather>
                            </ServerInitialConditions>
                            <ServerHandlers>
                                <FlatWorldGenerator generatorString="3;7,2;1;"/>
                                <DrawingDecorator>
                                    <DrawCuboid x1='-50' x2='50' y1='50' y2='50' z1='-50' z2='50' type='air'/>
                                    <DrawCuboid x1='-1' x2='2' y1='49' y2='49' z1='-50' z2='50' type='grass'/>
                                    <DrawCuboid x1='-1' x2='2' y1='48' y2='48' z1='-50' z2='50' type='air'/>
                                    <DrawCuboid x1='-1' x2='2' y1='47' y2='47' z1='-50' z2='50' type='stone'/>''' + \
                                    TNT_and_TRIGGERS + \
                                    Fence + \
                                '''</DrawingDecorator>
                                <ServerQuitWhenAnyAgentFinishes/>
                                <ServerQuitFromTimeUp timeLimitMs="1000000"/>
                                <ServerQuitWhenAnyAgentFinishes/>
                            </ServerHandlers>
                        </ServerSection>
               
                        <AgentSection mode="Survival">
                            <Name>CS175 mature AI demo</Name>
                            <AgentStart>
                                <Placement x="0.5" y="50" z="-49.5" pitch="45" yaw="0"/>
                                <Inventory>
                                    <InventoryItem slot="0" type="diamond_pickaxe"/>
                                </Inventory>
                            </AgentStart>
                            <AgentHandlers>
                                <DiscreteMovementCommands/>
                                <VideoProducer>
                                    <Width>860</Width>
                                    <Height>480</Height>
                                </VideoProducer>
                                <AgentQuitFromReachingCommandQuota total="20" />
                            </AgentHandlers>
                        </AgentSection>
                    </Mission>'''

    return missionXML


if __name__ == '__main__':
    agent_host = MalmoPython.AgentHost()

    malmoutils.parse_command_line(agent_host)

    my_mission = MalmoPython.MissionSpec(GetXML(), True)

    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

    recording_spec = MalmoPython.MissionRecordSpec()

    recording_spec.setDestination("recordings//agent_viewpoint.tgz")
    recording_spec.recordMP4(MalmoPython.FrameType.VIDEO, 24, 2000000, False)

    safeStartMission(agent_host, my_mission, client_pool, recording_spec, 0, '')
    safeWaitForStart([agent_host])

    world_state = agent_host.peekWorldState()

    # Loop until mission ends:
    while world_state.is_mission_running:

        agent_host.sendCommand("move 1")
        time.sleep(.5)

        world_state = agent_host.peekWorldState()

    print("Mission ended.")

    exit(1)