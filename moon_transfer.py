import krpc
import math
import time
def main():
    print("=== МИССИЯ: ОРБИТАЛЬНЫЙ ОБЛЁТ ЛУНЫ ===")
    print("Фаза 2: Перелёт к Муне")
    
    # Подключение к серверу kRPC
    try:
        conn = krpc.connect(name='Lunar Transfer')
        vessel = conn.space_center.active_vessel
        print("✓ Подключение к KSP установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return

    # Настройка потоковых данных
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    mun = conn.space_center.bodies['Mun']
    
    # Расчёт параметров перелёта
    print("Расчёт параметров перелёта...")
    
    # Получение текущей орбитальной скорости
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    v_orbit = math.sqrt(mu / r)
    
    # Расчёт Δv для перелёта к Муне (упрощённо)
    # В реальности используется более сложный расчёт с учётом положения Муны
    delta_v = 860  # м/с, из наших расчётов
    
    # Расчёт времени работы двигателя
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    
    print(f"Δv для перелёта: {delta_v:.0f} м/с")
    print(f"Время работы двигателя: {burn_time:.1f} с")

    # Поиск оптимального окна запуска (ожидание положения Муны)
    print("Ожидание оптимального положения Муны...")
    
    # Простая проверка - можно усложнить расчётом фазового угла
    time.sleep(5)  # В реальной миссии здесь сложная логика ожидания
    
    # Создание узла манёвра
    print("Создание узла манёвра...")
    node = vessel.control.add_node(ut() + 10, prograde=delta_v)
    
    # Ориентация для манёвра
    vessel.control.sas = False
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()
    
    # Ожидание времени манёвра
    print("Ожидание времени манёвра...")
    burn_ut = ut() + 10 - (burn_time / 2)
    while ut() < burn_ut:
        pass

    # Выполнение манёвра
    print("Выполнение манёвра перелёта к Муне!")
    vessel.control.throttle = 1.0
    
    # Регулировка тяги для точного выполнения манёвра
    remaining_burn = node.remaining_burn_vector(node.reference_frame)
    while remaining_burn[1] > 5:
        remaining_burn = node.remaining_burn_vector(node.reference_frame)
        time.sleep(0.1)
    
    # Тонкая корректировка
    while remaining_burn[1] > 0.5:
        vessel.control.throttle = 0.1
        remaining_burn = node.remaining_burn_vector(node.reference_frame)
    
    vessel.control.throttle = 0.0
    node.remove()
    
    print("✓ Манёвр перелёта к Муне завершён!")
    print("Время до достижения сферы влияния Муны: {} ч {} мин".format(
        int(vessel.orbit.time_to_soi_change // 3600),
        int((vessel.orbit.time_to_soi_change % 3600) // 60)))
    
    # Включение систем для длительного перелёта
    vessel.control.sas = True
    vessel.control.sas_mode = conn.space_center.SASMode.prograde
    
    print("✓ Фаза 2 завершена успешно!")
    print("Корабль следует к Муне по переходной траектории")
if __name__ == "__main__":
    main()