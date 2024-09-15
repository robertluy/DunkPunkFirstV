import asyncpg


async def connect_db():
    conn = await asyncpg.connect(
        user='postgres',
        password='Twer1432',
        database='helper_f',
        host='127.0.0.1',
        port=5432)
    return conn


async def start_db():
    conn = await connect_db()
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS students(
        tg_id INTEGER PRIMARY KEY,
        tg_tag VARCHAR(128) NOT NULL,
        chat_id INTEGER NOT NULL,
        course INTEGER NOT NULL,
        course_name VARCHAR(128) NOT NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS job_type(
        id SERIAL PRIMARY KEY,
        name VARCHAR(128) NOT NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS discipline(
        id SERIAL PRIMARY KEY,
        name VARCHAR(256) NOT NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS orders(
        id SERIAL PRIMARY KEY,
        period DATE NOT NULL,
        created DATE DEFAULT CURRENT_DATE,
        comment TEXT NOT NULL,
        stud_id INTEGER REFERENCES students(tg_id) ON DELETE SET NULL,
        status INTEGER,
        job_id INTEGER REFERENCES job_type(id) ON DELETE SET NULL,
        disc_id INTEGER REFERENCES discipline(id) ON DELETE SET NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS order_photo(
        id SERIAL PRIMARY KEY,
        ord_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        id_photo VARCHAR(256) NOT NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS order_documents(
        id SERIAL PRIMARY KEY,
        ord_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        id_document VARCHAR(256) NOT NULL)"""
    )

    await conn.execute(
        """CREATE TABLE IF NOT EXISTS solver(
        tg_id INTEGER PRIMARY KEY,
        tg_tag VARCHAR(128) NOT NULL,
        chat_id INTEGER NOT NULL,
        rating NUMERIC(2, 1) CHECK (rating >= 0 AND rating <= 5),
        course INTEGER NOT NULL,
        course_name VARCHAR(128) NOT NULL,
        phone VARCHAR(16) NOT NULL,
        bank VARCHAR(64) NOT NULL)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS presolution(
        id SERIAL PRIMARY KEY,
        sol_id INTEGER REFERENCES solver(tg_id) ON DELETE CASCADE,
        ord_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        price INTEGER NOT NULL,
        comment TEXT NOT NULL,
        status INTEGER)"""
    )
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS approved_discipline(
        id SERIAL PRIMARY KEY,
        sol_id INTEGER REFERENCES solver(tg_id) ON DELETE CASCADE,
        disc_id INTEGER REFERENCES discipline(id) ON DELETE CASCADE)"""
    )
    await conn.close()


async def check_user(tg_id):
    ret = [0, 0]
    conn = await connect_db()
    exist_st = await conn.fetch("SELECT tg_id FROM students WHERE tg_id=$1", tg_id)
    exist_sol = await conn.fetch("SELECT tg_id FROM solver WHERE tg_id=$1", tg_id)
    if exist_st:
        ret[0] = 1
    if exist_sol:
        ret[1] = 1
    await conn.close()
    return ret


async def add_student(dic):
    conn = await connect_db()
    ret = -1
    user_check = await check_user(dic['tg_id'])
    if user_check[0] == 0:
        print('not good')
        await conn.execute('''INSERT INTO students(tg_id, tg_tag, chat_id, course, course_name)
                              VALUES ($1, $2, $3, $4, $5)''',
                           dic['tg_id'], dic['tg_tag'], dic['chat_id'], int(dic['course']), dic['course_name'])
        ret = 1
    await conn.close()
    print('good')
    return ret


async def add_solver(dic):
    conn = await connect_db()
    ret = 1
    user_check = await check_user(dic['tg_id'])  # await добавлен
    if user_check[1] == 0:
        await conn.execute("INSERT INTO solver(tg_id, chat_id, rating, course, course_name, phone, bank)"
                           "VALUES ($1, $2, 0, $3, $4, $5, $6)",
                           dic['tg_id'], dic['chat_id'], dic['course'], dic['course_name'],
                           dic['phone'], dic['bank'])
        ret = -1
    await conn.close()
    return ret


async def update_solver_tg_tag(tg_id, tg_tag):
    conn = await connect_db()
    await conn.execute("UPDATE solver SET tg_tag=$1 WHERE tg_id=$2", tg_tag, tg_id)
    await conn.close()


async def get_solver_id_from_tg_tag(tg_tag):
    conn = await connect_db()
    ot = await conn.fetch("SELECT tg_id FROM solver WHERE tg_tag=$1", tg_tag)
    await conn.close()
    if ot:
        return ot[0][0]
    else:
        return -1


async def add_photo(dic):
    conn = await connect_db()
    ret = await conn.execute("INSERT INTO order_photo(ord_id, id_photo) VALUES($1, $2)",
                             dic['ord_id'], dic['photo'])
    await conn.close()
    return ret


async def add_document(dic):
    conn = await connect_db()
    ret = await conn.execute("INSERT INTO order_documents(ord_id, id_document) VALUES($1, $2)",
                             dic['ord_id'], dic['doc'])
    await conn.close()
    return ret


async def add_order(dic):
    conn = await connect_db()
    ret = await conn.fetchval("""INSERT INTO orders(period, comment, status, stud_id, job_id, disc_id)
                          VALUES(TO_DATE($1, 'YYYY-MM-DD'), $2, 0, $3, $4, $5) RETURNING id""",
                              dic['period'], dic['comment'], dic['stud_id'], dic['job_id'], dic['disc_id'])
    await conn.close()
    return ret


async def update_order_status(ord_id, status):
    conn = await connect_db()
    await conn.execute("UPDATE orders SET status=$1 WHERE id=$2", status, ord_id)
    await conn.close()


async def create_presolution(dic):
    conn = await connect_db()
    ret = await conn.fetchval("INSERT INTO presolution(sol_id, ord_id, price, comment, status)"
                              "VALUES ($1, $2, $3, $4, 0) RETURNING id",
                              dic['sol_id'], dic['ord_id'], dic['price'], dic['comment'])
    await conn.close()
    return ret


async def update_presolution_status(status, ord_id=0, id_=0):
    conn = await connect_db()
    if status == 1:
        await conn.execute("UPDATE presolution SET status=1 WHERE ord_id=$1", ord_id)
    elif status == 2:
        await conn.execute("UPDATE presolution SET status=2 WHERE ord_id=$1", ord_id)
        await update_order_status(ord_id, 0)
    elif status == 3:
        await conn.execute("UPDATE presolution SET status=$1 WHERE id=$2", status, id_)
        await conn.execute("UPDATE presolution SET status=1 WHERE ord_id=$1 AND id!=$2", ord_id, id_)
    else:
        await conn.execute("UPDATE presolution SET status=$1 WHERE id=$2", status, id_)
    await conn.close()


async def show_presolution_student(stud_id):
    conn = await connect_db()
    sps = [[-1]]
    sps_tmp = await conn.fetch(
        """
        SELECT o.id, p.sol_id, d.name, p.price, p.comment, p.status
        FROM presolution p
        LEFT JOIN orders o ON p.ord_id = o.id
        LEFT JOIN discipline d ON o.disc_id = d.id
        WHERE o.stud_id = $1 AND (p.status = 0 OR p.status = 3)
        """,
        stud_id
    )
    if sps_tmp:
        sps = [list(i) for i in sps_tmp]
    await conn.close()
    return sps


async def show_solver_order_stat(sol_id, ord_id):
    conn = await connect_db()
    sps = [-1]
    sps_tmp = await conn.fetch("SELECT id, price, comment, status FROM presolution WHERE ord_id=$1 AND sol_id=$2",
                               ord_id, sol_id)
    if sps_tmp:
        sps = list(sps_tmp[0])
    await conn.close()
    return sps


async def show_solver_completed(sol_id):
    conn = await connect_db()
    sps = [-1]
    sps_tmp = await conn.fetch(
        "SELECT o.id, o.period, o.comment, o.stud_id, o.job_id "
        "FROM orders o LEFT JOIN presolution p "
        "ON o.id=p.ord_id "
        "WHERE p.sol_id=$1 AND p.status=4",
        sol_id)
    if sps_tmp:
        sps = [list(i) for i in sps_tmp]
    await conn.close()
    return sps


async def show_solver_not_completed(sol_id):
    conn = await connect_db()
    sps = [-1]
    sps_tmp = await conn.fetch(
        "SELECT o.id, o.period, o.comment, o.stud_id, o.job_id "
        "FROM orders o LEFT JOIN presolution p "
        "ON o.id=p.ord_id "
        "WHERE p.sol_id=$1 AND p.status=3",
        sol_id)
    if sps_tmp:
        sps = [list(i) for i in sps_tmp]
    await conn.close()
    return sps


async def show_solver_rejected(sol_id):
    conn = await connect_db()
    sps = [-1]
    sps_tmp = await conn.fetch(
        "SELECT o.id, o.period, o.comment, o.stud_id, o.job_id "
        "FROM orders o LEFT JOIN presolution p "
        "ON o.id=p.ord_id "
        "WHERE p.sol_id=$1 AND (p.status=1 OR p.status=2)",
        sol_id)
    if sps_tmp:
        sps = [list(i) for i in sps_tmp]
    await conn.close()
    return sps


async def approve_solver_dic(sol_id, disc_id):
    conn = await connect_db()
    await conn.execute("INSERT INTO approved_discipline(sol_id, disc_id) VALUES ($1, $2)", sol_id, disc_id)
    await conn.close()


async def show_disc_id():
    conn = await connect_db()
    sps = [-1]
    sps_tmp = await conn.fetch("SELECT id, name FROM discipline")
    if sps_tmp:
        sps = [list(i) for i in sps_tmp]
    await conn.close()
    return sps


async def check_approve(sol_id, disc_id):
    conn = await connect_db()
    o = 0
    sps_tmp = await conn.fetch("SELECT id FROM approved_discipline WHERE sol_id=$1 AND disc_id=$2", sol_id, disc_id)
    if sps_tmp:
        o = 1
    await conn.close()
    return o


async def show_orders(sol_id, disc_id):
    approved = await check_approve(sol_id, disc_id)
    if approved:
        conn = await connect_db()
        sps = [-1]
        sps_tmp = await conn.fetch("""
        SELECT o.id, o.period, o.created, o.comment, j.name, od.id_document, op.id_photo
        FROM orders o
        LEFT JOIN job_type j ON o.job_id=j.id
        LEFT JOIN order_documents od ON od.ord_id=o.id
        LEFT JOIN order_photo op ON op.ord_id=o.id
        LEFT JOIN presolution pr ON pr.ord_id=o.id
        WHERE pr.status=1
        """)
        if sps_tmp:
            sps = [list(i) for i in sps_tmp]
        await conn.close()
        return sps
    else:
        return [-1]


async def show_job_type(id):
    conn = await connect_db()
    ot = 'None'
    jn = await conn.fetch("SELECT name FROM job_type WHERE id=$1", id)
    if jn:
        ot = jn[0][0]
    await conn.close()
    return ot


async def show_disc_name(id):
    conn = await connect_db()
    ot = 'None'
    jn = await conn.fetch("SELECT name FROM discipline WHERE id=$1", id)
    if jn:
        ot = jn[0][0]
    await conn.close()
    return ot
