import json
import os
from datetime import date, datetime, timedelta

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.clock import Clock

WORKOUTS = {
    "A": {
        "name": "Верх + пресс",
        "day": "Понедельник",
        "color": [0.66, 0.33, 0.97, 1],
        "exercises": [
            {"name": "Отжимания сложные", "sets": 4, "reps": "8–15"},
            {"name": "Тяга резинки к поясу", "sets": 4, "reps": "12–20"},
            {"name": "Pike push-ups", "sets": 3, "reps": "8–15"},
            {"name": "Жим резинки от груди", "sets": 3, "reps": "15–20"},
            {"name": "Махи гантелями 4 lb", "sets": 3, "reps": "20–30"},
            {"name": "Бицепс + трицепс", "sets": 3, "reps": "15–20"},
            {"name": "Планка", "sets": 3, "reps": "60 сек"},
            {"name": "Hollow body hold", "sets": 3, "reps": "30 сек"},
            {"name": "Dead bug", "sets": 3, "reps": "10 на сторону"},
        ],
    },
    "B": {
        "name": "Низ + пресс",
        "day": "Среда",
        "color": [0.93, 0.28, 0.60, 1],
        "exercises": [
            {"name": "Болгарские выпады", "sets": 4, "reps": "10–15 на ногу"},
            {"name": "Приседания сложные", "sets": 4, "reps": "8–15"},
            {"name": "Румынская тяга на одной ноге", "sets": 3, "reps": "12 на ногу"},
            {"name": "Ягодичный мост одной ногой", "sets": 3, "reps": "15"},
            {"name": "Боковые выпады", "sets": 3, "reps": "12"},
            {"name": "Икры", "sets": 4, "reps": "20–30"},
            {"name": "Подъёмы ног", "sets": 3, "reps": "15"},
            {"name": "Reverse crunch", "sets": 3, "reps": "15"},
            {"name": "Боковая планка", "sets": 3, "reps": "40 сек"},
        ],
    },
    "C": {
        "name": "Круг + кардио",
        "day": "Пятница",
        "color": [0.13, 0.83, 0.93, 1],
        "exercises": [
            {"name": "Круг x4: 10 бурпи", "sets": 4, "reps": "10"},
            {"name": "Круг x4: 15 отжиманий", "sets": 4, "reps": "15"},
            {"name": "Круг x4: 20 приседов", "sets": 4, "reps": "20"},
            {"name": "Круг x4: 15 тяга резинки", "sets": 4, "reps": "15"},
            {"name": "Круг x4: 30 сек mountain climbers", "sets": 4, "reps": "30 сек"},
            {"name": "Круг x4: 20 Russian twist", "sets": 4, "reps": "20"},
            {"name": "Кардио 15–20 мин", "sets": 1, "reps": "30/30"},
            {"name": "Bicycle crunch", "sets": 3, "reps": "20"},
            {"name": "Leg raises", "sets": 3, "reps": "15"},
            {"name": "Планка", "sets": 3, "reps": "60 сек"},
        ],
    },
}

class Store:
    def __init__(self):
        self.path = os.path.join(MDApp.get_running_app().user_data_dir, "workout_data.json")
        self.data = {"history": {}, "weights": {}}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_session(self, key, done, total):
        d = date.today().isoformat()
        self.data["history"].setdefault(d, [])
        self.data["history"][d].append({
            "workout": key, "name": WORKOUTS[key]["name"],
            "done": done, "total": total,
            "time": datetime.now().strftime("%H:%M"),
        })
        self.save()

    def add_weight(self, kg):
        self.data["weights"][date.today().isoformat()] = kg
        self.save()

    def streak(self):
        days = set(self.data["history"].keys())
        if not days:
            return 0
        count = 0
        d = date.today()
        if d.isoformat() not in days:
            d -= timedelta(days=1)
        while d.isoformat() in days:
            count += 1
            d -= timedelta(days=1)
        return count

    def total_sessions(self):
        return sum(len(v) for v in self.data["history"].values())

class DashboardScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "dashboard"
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(title="FitTrack", elevation=4))
        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", padding=dp(16),
                              spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        self.date_label = MDLabel(text="", font_style="Subtitle1",
                                  theme_text_color="Secondary",
                                  size_hint_y=None, height=dp(30))
        content.add_widget(self.date_label)
        cards = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                            size_hint_y=None, height=dp(100))
        self.streak_card = self._stat_card("Серия", "0", [0.66, 0.33, 0.97, 1])
        self.total_card = self._stat_card("Всего", "0", [0.93, 0.28, 0.60, 1])
        self.week_card = self._stat_card("Неделя", "0", [0.13, 0.83, 0.93, 1])
        cards.add_widget(self.streak_card)
        cards.add_widget(self.total_card)
        cards.add_widget(self.week_card)
        content.add_widget(cards)
        content.add_widget(MDLabel(text="Быстрый старт", font_style="H6",
                                   size_hint_y=None, height=dp(40)))
        for key in ("A", "B", "C"):
            btn = MDRaisedButton(
                text=f"Тренировка {key} — {WORKOUTS[key]['name']}",
                size_hint_y=None, height=dp(56),
                md_bg_color=WORKOUTS[key]["color"],
                on_release=lambda x, k=key: self.go_workout(k))
            content.add_widget(btn)
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _stat_card(self, label, value, color):
        card = MDCard(orientation="vertical", padding=dp(12),
                      radius=[dp(12)], md_bg_color=color)
        card.add_widget(MDLabel(text=label, theme_text_color="Custom",
                                text_color=[1, 1, 1, 1], font_style="Caption"))
        val = MDLabel(text=value, theme_text_color="Custom",
                      text_color=[1, 1, 1, 1], font_style="H5")
        card.add_widget(val)
        card.value_label = val
        return card

    def go_workout(self, key):
        self.manager.current = "workouts"
        self.manager.get_screen("workouts").select(key)

    def refresh(self):
        s = self.manager.app.store
        self.date_label.text = date.today().strftime("%d.%m.%Y")
        self.streak_card.value_label.text = f"{s.streak()} дн."
        self.total_card.value_label.text = str(s.total_sessions())

class WorkoutsScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "workouts"
        self.current = "A"
        self.checkboxes = []
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(
            title="Тренировки", elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]]))
        tab_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                              height=dp(56), padding=dp(8), spacing=dp(8))
        self.tab_buttons = {}
        for key in ("A", "B", "C"):
            btn = MDFlatButton(text=f"{key}", on_release=lambda x, k=key: self.select(k))
            tab_bar.add_widget(btn)
            self.tab_buttons[key] = btn
        root.add_widget(tab_bar)
        self.scroll = MDScrollView()
        self.exercise_list = MDList()
        self.scroll.add_widget(self.exercise_list)
        root.add_widget(self.scroll)
        footer = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                             height=dp(70), padding=dp(12), spacing=dp(12))
        self.counter = MDLabel(text="Выполнено: 0/0", font_style="Body2")
        footer.add_widget(self.counter)
        footer.add_widget(MDRaisedButton(text="Сохранить",
                                         md_bg_color=[0.48, 0.23, 0.93, 1],
                                         on_release=lambda x: self.save()))
        root.add_widget(footer)
        self.add_widget(root)

    def go_back(self):
        self.manager.current = "dashboard"

    def select(self, key):
        self.current = key
        self.build_list()

    def build_list(self):
        self.exercise_list.clear_widgets()
        self.checkboxes = []
        for ex in WORKOUTS[self.current]["exercises"]:
            row = MDCard(orientation="horizontal", size_hint_y=None,
                         height=dp(80), padding=dp(8), radius=[dp(8)])
            item = {"check": None, "done": False, "ex": ex}
            check = MDIconButton(icon="checkbox-blank-outline")
            item["check"] = check
            check.bind(on_release=lambda x, it=item: self.toggle(it))
            row.add_widget(check)
            info = MDBoxLayout(orientation="vertical")
            info.add_widget(MDLabel(text=ex["name"], font_style="Body1"))
            info.add_widget(MDLabel(text=f"{ex['sets']} x {ex['reps']}",
                                    theme_text_color="Secondary",
                                    font_style="Caption"))
            row.add_widget(info)
            self.exercise_list.add_widget(row)
            self.checkboxes.append(item)
        self.update_counter()

    def toggle(self, item):
        item["done"] = not item["done"]
        item["check"].icon = "checkbox-marked" if item["done"] else "checkbox-blank-outline"
        self.update_counter()

    def update_counter(self):
        done = sum(1 for c in self.checkboxes if c["done"])
        self.counter.text = f"Выполнено: {done}/{len(self.checkboxes)}"

    def save(self):
        done_names = [c["ex"]["name"] for c in self.checkboxes if c["done"]]
        if not done_names:
            return
        self.manager.app.store.add_session(self.current, done_names, len(self.checkboxes))
        self.select(self.current)

    def refresh(self):
        self.select(self.current)

class HistoryScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "history"
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(title="История", elevation=4,
                                    left_action_items=[["arrow-left", lambda x: self.go_back()]]))
        self.scroll = MDScrollView()
        self.list = MDList()
        self.scroll.add_widget(self.list)
        root.add_widget(self.scroll)
        self.add_widget(root)

    def go_back(self):
        self.manager.current = "dashboard"

    def refresh(self):
        self.list.clear_widgets()
        hist = self.manager.app.store.data["history"]
        if not hist:
            self.list.add_widget(OneLineListItem(text="Пока нет записей"))
            return
        for d in sorted(hist.keys(), reverse=True):
            for e in hist[d]:
                pct = round(len(e["done"]) / e["total"] * 100) if e["total"] else 0
                self.list.add_widget(TwoLineListItem(
                    text=f"{d} — Тренировка {e['workout']}",
                    secondary_text=f"{len(e['done'])}/{e['total']} ({pct}%)"))

class WeightScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "weight"
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(title="Вес", elevation=4,
                                    left_action_items=[["arrow-left", lambda x: self.go_back()]]))
        content = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                          size_hint_y=None, height=dp(60))
        self.weight_input = MDTextField(hint_text="Введи вес (кг)", input_filter="float")
        row.add_widget(self.weight_input)
        row.add_widget(MDRaisedButton(text="+ Записать", on_release=lambda x: self.add_weight()))
        content.add_widget(row)
        self.scroll = MDScrollView()
        self.list = MDList()
        self.scroll.add_widget(self.list)
        content.add_widget(self.scroll)
        root.add_widget(content)
        self.add_widget(root)

    def go_back(self):
        self.manager.current = "dashboard"

    def add_weight(self):
        try:
            kg = float(self.weight_input.text.replace(",", "."))
        except ValueError:
            return
        self.manager.app.store.add_weight(kg)
        self.weight_input.text = ""
        self.refresh()

    def refresh(self):
        self.list.clear_widgets()
        weights = self.manager.app.store.data["weights"]
        for d in sorted(weights.keys(), reverse=True):
            self.list.add_widget(OneLineListItem(text=f"{d} — {weights[d]} кг"))

class FitTrackApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.store = Store()
        sm = MDScreenManager()
        sm.app = self
        self.screens = {
            "dashboard": DashboardScreen(),
            "workouts": WorkoutsScreen(),
            "history": HistoryScreen(),
            "weight": WeightScreen(),
        }
        for name, screen in self.screens.items():
            sm.add_widget(screen)
        sm.current = "dashboard"
        return sm

if __name__ == "__main__":
    FitTrackApp().run()
