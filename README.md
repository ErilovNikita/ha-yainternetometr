# ha-yainternetometr
> Интеграция для Home Assistant для измерения скорости интернета, на базе Я.Интернетометр.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/ErilovNikita/ha-yainternetometr?label=Latest%20Release&color)](https://github.com/ErilovNikita/ha-yainternetometr/releases/latest)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-green.svg)](https://github.com/hacs/default)
[![HACS Validate](https://github.com/ErilovNikita/ha-yainternetometr/actions/workflows/hacs-validate.yml/badge.svg?branch=main)](https://github.com/ErilovNikita/ha-yainternetometr/actions/workflows/hacs-validate.yml)

<p align="center" float="center" width="100%">
  <img src="docs/img/icon.svg" width="20%" /> 
  &nbsp;
  &nbsp;
  &nbsp;
  &nbsp;
  &nbsp;
  &nbsp;
  <img src="https://github.com/home-assistant/brands/blob/master/core_integrations/_homeassistant/icon.png?raw=true" width="20%" />
</p>

Данная интеграция предоставляет возможность проводить измерения скорости интернета на базе проб сервиса Я.Интернетометр.

Данная интеграция работает на базе  библиотеке [yaspeedtest](https://github.com/ErilovNikita/yaspeedtest).

> [!WARNING]  
> Данная интеграция является НЕ официальной, и не пытается ей казаться. Данная интеграция разрабатывается исключительно в личных интересах, и использует только общедоступные endpoint'ы.

## Установка
### Автоматически
> [!TIP]  
> Рекомендуемый способ установки

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ErilovNikita&repository=ha-yainternetometr&category=integration)

1. Через интерфейс HACS найдите `YaInternetometr`
2. Установите интеграцию

### Вручную
Клонируйте репозиторий во временный каталог, затем переместите по пути `custom_components/yainternetometr`
``` bash
git clone https://github.com/ErilovNikita/ha-yainternetometr.git
mkdir -p /mnt/homeassistant/config/custom_components
mv ha-yainternetometr/custom_components/yainternetometr /config/custom_components/
```

## Конфигурация
### Автоматически
[![​Open your Home Assistant instance and start setting up a new integration.​](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=yainternetometr)

### Вручную
1. Откройте `Настройки` -> `Интеграции`
1. Нажмите внизу справа страницы кнопку с плюсом
1. Введите в поле поиска `YaInternetometr`
1. Выберите первый результат из списка
1. Нажмите кнопку `Продолжить`
2. 🎉 Готово! 

## License
Данный проект лицензирован по лицензии Apache 2.0 — подробности см. в файле [LICENSE](LICENSE).