import krpc
import math
import time
def main():
    print("=== МИССИЯ: ОРБИТАЛЬНЫЙ ОБЛЁТ ЛУНЫ ===")
    print("Фаза 3: Облёт Муны")
    
    # Подключение к серверу kRPC
    try:
        conn = krpc.connect(name='Lunar Flyby')
        vessel = conn.space_center.active_vessel
        print("✓ Подключение к KSP установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return

    # Настройка потоковых данных
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    mun = conn.space_center.bodies['Mun']
    
    print("Ожидание входа в сферу влияния Муны...")
    
    # Ожидание перехода в SOI Муны
    while vessel.orbit.body.name != 'Mun':
        pass
    
    print("✓ Вход в сферу влияния Муны!")
    
    # Получение параметров орбиты относительно Муны
    periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    time_to_periapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
    
    print(f"Периапсис относительно Муны: {periapsis() / 1000:.1f} км")
    print(f"Время до периапсиса: {time_to_periapsis() / 60:.1f} мин")
    
    # Коррекция траектории для обеспечения безопасного пролёта
    target_periapsis = 50000  # 50 км
    
    if periapsis() < 30000 or periapsis() > 100000:
        print("Требуется коррекция траектории...")
        
        # Расчёт Δv для коррекции
        delta_v = 50  # м/с, эмпирически
        
        # Создание узла манёвра
        node = vessel.control.add_node(ut() + 10, normal=delta_v)
        
        # Ориентация и выполнение манёвра
        vessel.control.sas = False
        vessel.auto_pilot.engage()
        vessel.auto_pilot.reference_frame = node.reference_frame
        vessel.auto_pilot.target_direction = (0, 0, 1)
        vessel.auto_pilot.wait()
        
        # Выполнение манёвра
        vessel.control.throttle = 1.0
        time.sleep(2)  # Упрощённо
        vessel.control.throttle = 0.0
        node.remove()
        
        print("✓ Коррекция траектории выполнена")
    
    # Ожидание пролёта периапсиса
    print("Ожидание пролёта периапсиса...")
    while time_to_periapsis() > 0:
        pass
    
    print("✓ Пролёт периапсиса! Высота: {} км".format(
        int(periapsis() / 1000)))
    
    # Фотографирование (симуляция)
    print("Активация научных приборов...")
    time.sleep(3)
    print("✓ Сбор данных о поверхности Муны завершён")
    
    print("✓ Фаза 3 завершена успешно!")
    print("Корабль завершил облёт Муны и выходит из сферы влияния")
if __name__ == "__main__":
        main()
