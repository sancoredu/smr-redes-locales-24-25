"""
Discusión: Simulador de CSMA/CD (Carrier Sense Multiple Access with Collision Detection)
========================================================================================
Unidad 4: Interconexión de equipos en Redes Locales
Redes Locales - SMR
Curso 2024-2025
IES Antonio Sequeros

1. Analiza el código del método Workstation::communicate() y describe cómo se relaciona con el diagrama de flujo de la
diapositiva 28 de la Unidad 4.
2. Ejecuta el script y analiza el resultado.
3. Completa el código de la estrategia de _backoff_, ejecuta de nuevo el script y analiza el resultado.
4. Ejecuta el script con diferentes valores para los parámetros `workstation_count` y `attempt_max_count`, representa
gráficamente los resultados obtenidos y analízalos.
"""

import random
import sys
from typing import Any, Generator


class Medium:
    def __init__(self):
        self.msg_current = []
        self.msg_next = []
        self.collision_count = 0

    def is_idle(self) -> bool:
        return len(self.msg_current) == 0

    def is_collision(self) -> bool:
        return len(self.msg_current) > 1


class Workstation:

    def __init__(self, _id):
        self._id = _id

        self.msg_requested_count = 0
        self.msg_sent_count = 0
        self.msg_sent_success_count = 0
        self.msg_sent_collided_count = 0
        self.msg_discarded_count = 0

    @property
    def name(self) -> str:
        return f"ws-{self._id:0>3}"

    def communicate(
        self, medium: Medium, msg_requested_count: int, attempt_max_count: int
    ) -> Generator[None, Any, Any]:
        self.msg_requested_count = msg_requested_count
        msg_requested_i = 0

        while msg_requested_i < msg_requested_count:
            if random.randint(0, 9) >= 5:
                print(f"{self.name} | No messages to transmit, idling...")
                yield

            else:
                msg_requested_i += 1

                for attempt_current_count in range(1, attempt_max_count + 1):
                    while not medium.is_idle():
                        print(
                            f"{self.name} | Medium is busy. Waiting until the medium is idle..."
                        )
                        yield

                    print(f"{self.name} | Medium is idle. Sending message...")
                    medium.msg_next.append("message")
                    self.msg_sent_count += 1
                    yield

                    if medium.is_collision():
                        print(
                            f"{self.name} | Collision detected. Sending jam signal: 10101010 10101010 10101010 10101010..."
                        )
                        self.msg_sent_collided_count += 1
                        medium.collision_count += 1 / len(medium.msg_current)

                        # TODO: Implement backoff
                        slot_times_to_wait = 0

                        if slot_times_to_wait == 0:
                            print(
                                f"{self.name} | Waiting 0 slot times before restarting process..."
                            )

                        else:
                            for slot_times_remaining in reversed(
                                range(1, slot_times_to_wait + 1)
                            ):
                                print(
                                    f"{self.name} | Waiting {slot_times_remaining} more slot times before restarting process..."
                                )
                                yield

                        yield

                    else:
                        print(f"{self.name} | Message successfully sent")
                        self.msg_sent_success_count += 1
                        yield
                        break

                else:
                    print(f"{self.name} | All attempts exhausted, message discarded")
                    self.msg_discarded_count += 1


def main():
    medium = Medium()
    workstations = list()
    communications = list()

    msg_requested_count = 1_000
    workstation_count = 10
    attempt_max_count = 10

    for i in range(1, workstation_count + 1):
        workstation = Workstation(i)
        workstations.append(workstation)
        communications.append(
            workstation.communicate(medium, msg_requested_count, attempt_max_count)
        )

    while len(communications):
        for comm_index, communication in enumerate(communications):
            try:
                next(communication)
            except StopIteration:
                del communications[comm_index]

        medium.msg_current = medium.msg_next.copy()
        medium.msg_next = list()

    msg_requested_count = sum(
        workstation.msg_requested_count for workstation in workstations
    )
    msg_sent_count = sum(workstation.msg_sent_count for workstation in workstations)
    msg_sent_success_count = sum(
        workstation.msg_sent_success_count for workstation in workstations
    )
    msg_sent_collided_count = sum(
        workstation.msg_sent_collided_count for workstation in workstations
    )
    msg_discarded_count = sum(
        workstation.msg_discarded_count for workstation in workstations
    )

    print(f"Stats")
    print(f"=====")
    print(f"* Number of workstations: {workstation_count}")
    print(f"* Maximum number of attempts: {attempt_max_count}")

    print(f"* Total messages requested: {msg_requested_count:_}")
    print(f"  * Sent: {msg_sent_count:_}")
    print(
        f"    * Collided: {msg_sent_collided_count:_} ({msg_sent_collided_count / msg_sent_count * 100:.2f}%) in {medium.collision_count:_.0f} collisions"
    )
    print(
        f"  * Successfully delivered: {msg_sent_success_count:_} ({msg_sent_success_count / msg_requested_count * 100:.2f}%)"
    )
    print(
        f"  * Discarded: {msg_discarded_count:_} ({msg_discarded_count / msg_requested_count * 100:.2f}%)"
    )


if __name__ == "__main__":
    sys.exit(main())
