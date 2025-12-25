import krpc
import math
import time
def main():
    print("=== МИССИЯ: ОРБИТАЛЬНЫЙ ОБЛЁТ ЛУНЫ ===")
    print("Фаза 1: Старт и вывод на орбиту Кербина")
    
    # Подключение к серверу kRPC
    try:
        conn = krpc.connect(name='Lunar Flyby Mission')
        vessel = conn.space_center.active_vessel
        print("✓ Подключение к KSP установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return

    # Настройка потоковых данных
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
    solid_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')

    # Параметры миссии
    target_altitude = 100000  # 100 км
    turn_start_altitude = 1000
    turn_end_altitude = 45000
    heading = 90  # Восток

    # Предстартовая подготовка
    print("Предстартовая подготовка...")
    vessel.control.sas = False
    vessel.control.rcs = False
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, heading)

    # Запуск двигателей
    print("Запуск двигателей! T-0")
    vessel.control.throttle = 1.0
    time.sleep(0.5)
    vessel.control.activate_next_stage()

    # Вертикальный подъём
    while altitude() < turn_start_altitude:
        pass

    # Гравитационный разворот
    print("Начало гравитационного разворота")
    turn_angle = 0
    while altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) / 
                (turn_end_altitude - turn_start_altitude))
        new_pitch = 90 * (1 - frac)
        vessel.auto_pilot.target_pitch_and_heading(new_pitch, heading)
        time.sleep(0.1)

    # Ожидание отделения ускорителей
    print("Ожидание отделения ускорителей...")
    while solid_fuel() > 0.1:
        pass
    vessel.control.activate_next_stage()
    print("✓ Ускорители отделены")

    # Вывод на орбиту
    print("Вывод на орбиту...")
    vessel.auto_pilot.target_pitch_and_heading(0, heading)
    
    # Ожидание достижения целевого апогея
    while apoapsis() < target_altitude:
        pass
    
    print("✓ Достигнут целевой апогей, завершение работы двигателей")
    vessel.control.throttle = 0.0

    # Планирование манёвра для округления орбиты
    print("Планирование манёвра округления орбиты...")
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2.0 / r) - (1.0 / a1)))
    v2 = math.sqrt(mu * ((2.0 / r) - (1.0 / a2)))
    delta_v = v2 - v1
    
    # Расчёт времени работы двигателя
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    # Создание узла манёвра
    node = vessel.control.add_node(ut() + vessel.orbit.time_to_apoapsis, 
                                  prograde=delta_v)
    
    # Ориентация для манёвра
    print("Ориентация корабля...")
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()

    # Ожидание времени манёвра
    print("Ожидание времени манёвра...")
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.0)
    while ut() < burn_ut:
        pass

    # Выполнение манёвра
    print("Выполнение манёвра округления орбиты")
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 0.1)
    print("Тонкая корректировка...")
    remaining_burn = node.remaining_burn_vector(node.reference_frame)
    while remaining_burn[1] > 0.5:
        vessel.control.throttle = 0.2
        remaining_burn = node.remaining_burn_vector(node.reference_frame)
    vessel.control.throttle = 0.0

    # Завершение манёвра
    node.remove()
    print("✓ Орбита округлена! Высота орбиты: {} км".format(
        int(apoapsis() / 1000)))
    
    # Отделение второй ступени
    print("Отделение второй ступени...")
    vessel.control.activate_next_stage()
    time.sleep(1)
    
    # Включение систем
    vessel.control.sas = True
    vessel.control.sas_mode = conn.space_center.SASMode.stability_assist
    
    print("✓ Фаза 1 завершена успешно!")
    print("Корабль находится на стабильной орбите Кербина")
if __name__ == "__main__":
    main()
