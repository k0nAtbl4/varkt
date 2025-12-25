import krpc
import math
import time


def main():
    print("=== МИССИЯ: ОРБИТАЛЬНЫЙ ОБЛЁТ ЛУНЫ ===")
    print("Фаза 4: Возвращение на Кербин")

    # Подключение к серверу kRPC
    try:
        conn = krpc.connect(name="Return to Kerbin")
        vessel = conn.space_center.active_vessel
        print("✓ Подключение к KSP установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return

    # Настройка потоковых данных
    ut = conn.add_stream(getattr, conn.space_center, "ut")
    altitude = conn.add_stream(getattr, vessel.flight(), "mean_altitude")

    print("Ожидание выхода из сферы влияния Муны...")

    # Ожидание возвращения в SOI Кербина
    while vessel.orbit.body.name == "Mun":
        pass

    print("✓ Возвращение в сферу влияния Кербина!")

    # Расчёт манёвра для возвращения
    print("Расчёт траектории возвращения...")

    # Получение параметров периапсиса относительно Кербина
    periapsis = conn.add_stream(getattr, vessel.orbit, "periapsis_altitude")
    time.sleep(2)  # Ждём стабилизации орбитальных параметров

    current_periapsis = periapsis()
    print(f"Текущий периапсис: {current_periapsis / 1000:.1f} км")

    # Если периапсис слишком высок, выполняем коррекцию
    if current_periapsis > 40000:
        print("Требуется коррекция траектории для входа в атмосферу...")

        # Расчёт Δv для уменьшения периапсиса
        delta_v = 100  # м/с

        # Создание узла манёвра (торможение)
        node = vessel.control.add_node(
            ut() + vessel.orbit.time_to_periapsis, retrograde=delta_v
        )

        # Расчёт времени работы двигателя
        F = vessel.available_thrust
        Isp = vessel.specific_impulse * 9.82
        m0 = vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        # Ориентация для манёвра
        vessel.control.sas = False
        vessel.auto_pilot.engage()
        vessel.auto_pilot.reference_frame = node.reference_frame
        vessel.auto_pilot.target_direction = (0, -1, 0)
        vessel.auto_pilot.wait()

        # Ожидание времени манёвра
        burn_ut = ut() + vessel.orbit.time_to_periapsis - (burn_time / 2)
        while ut() < burn_ut:
            pass

        # Выполнение манёвра
        print("Выполнение манёвра коррекции траектории...")
        vessel.control.throttle = 1.0
        time.sleep(burn_time)
        vessel.control.throttle = 0.0
        node.remove()

        print("✓ Коррекция траектории выполнена")
        print(f"Новый периапсис: {periapsis() / 1000:.1f} км")

    # Ожидание входа в атмосферу
    print("Ожидание входа в атмосферу...")
    while altitude() > 70000:
        pass

    print("✓ Начало атмосферного торможения!")

    # Ориентация для тепловой защиты
    vessel.control.sas = True
    vessel.control.sas_mode = conn.space_center.SASMode.retrograde

    # Ожидание снижения скорости
    speed = conn.add_stream(getattr, vessel.flight(), "speed")
    while speed() > 200:
        pass

    # Отделение служебного модуля
    print("Отделение служебного модуля...")
    vessel.control.activate_next_stage()

    # Ожидание раскрытия парашютов
    while altitude() > 5000:
        pass

    print("Раскрытие парашютов...")
    vessel.control.activate_next_stage()

    # Ожидание посадки
    while vessel.situation != conn.space_center.VesselSituation.landed:
        pass

    print("✓ ПОСАДКА! Миссия завершена успешно!")
    print("Орбитальный облёт Луны выполнен!")


if __name__ == "__main__":
    main()
