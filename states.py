from aiogram.dispatcher.filters.state import State, StatesGroup


class StudentDisciplineChoice(StatesGroup):
    discipline_list = State()
    period = State()
    comment = State()
    job_type = State()
    photo = State()
    finalize = State()
    confirmation = State()


class RegistrationStudent(StatesGroup):
    course = State()
    course_name = State()


class RegistrationSolver(StatesGroup):
    course = State()
    course_name = State()
    phone = State()
    bank = State()
