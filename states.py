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
    phone = State()
    bank = State()
    course_name = State()


class CheckingOpenOrders(StatesGroup):
    disc = State()
    order = State()
    price = State()
    comment = State()


class LookAtStatusesSolver(StatesGroup):
    waiting = State()


class Admin_Approve(StatesGroup):
    discipline_list = State()
    solver_name = State()


# class SolverOrders(StatesGroup):

class ChatTmp(StatesGroup):
    savage = State()
    active = State()


class RemoveOrder(StatesGroup):
    removing = State()


class AdminSendSolution(StatesGroup):
    ord = State()
    end = State()
