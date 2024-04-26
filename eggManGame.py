import psycopg2


def get_conn():
    return psycopg2.connect()
 

def set_correct_ans(user_id, correct_ans):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET correct_ans = %s WHERE user_id = %s", (correct_ans, user_id))
    conn.commit()
 
 
def get_correct_ans(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT correct_ans FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()[0]
 
 
def set_egg_ammount(user_id, egg_ammount):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET egg_ammount = %s WHERE user_id = %s", (egg_ammount, user_id))
    conn.commit()
 
 
def get_egg_ammount(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT egg_ammount FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()[0]
 
 
def clear_user_answers(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM answers WHERE user_id = %s", (user_id,))
    conn.commit()
 
 
def append_user_answers(user_id, answer):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (user_id, answer) VALUES (%s, %s)", (user_id, answer))
    conn.commit()
 
 
def get_user_answers(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM answers WHERE user_id = %s", (user_id,))
    result = cursor.fetchall()
    return [int(row[0]) for row in result]
 
 
def get_user_last_answer(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM answers WHERE user_id = %s ORDER BY id DESC", (user_id,))
    return int(cursor.fetchone()[0])
 
 
def set_user_best_score(user_id, score):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET best_score = %s WHERE user_id = %s", (score, user_id))
    conn.commit()
 
 
def get_user_best_score(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT best_score FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()[0]
 
 
def get_top_users():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, best_score FROM users ORDER BY best_score DESC")
    return [(int(_[0]), int(_[1])) for _ in cursor.fetchall()]
 
 
def set_user_state(user_id, state):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET user_state = %s WHERE user_id = %s", (state, user_id))
    conn.commit()
 
 
def get_user_state(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_state FROM users WHERE user_id=%s", (user_id,))
    return cursor.fetchone()[0]
 
 
def set_round(user_id, test_group):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET round=%s WHERE user_id=%s", (test_group, user_id))
    conn.commit()
 
 
def get_round(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT round FROM users WHERE user_id=%s", (user_id,))
    return cursor.fetchone()[0]
 
 
def count_score(user_id):
    user_ans_list = get_user_answers(user_id)
    correct_ans = get_correct_ans(user_id)
    best_solve_list = [14, 27, 39, 50, 60, 69, 77, 84, 90, 95, 99]
    correct_ans_list = []
    for _ in best_solve_list:
        if correct_ans < _:
            if correct_ans_list:
                correct_ans_list.append(_)
                correct_ans_list.extend(range(correct_ans_list[-2]+1, correct_ans+1))
            else:
                correct_ans_list = [14]
                correct_ans_list.extend(range(1, correct_ans+1))
            break
        elif correct_ans == _:
            correct_ans_list.append(_)
            break
        correct_ans_list.append(_)
 
    score = int(1000 * min(len(user_ans_list), len(correct_ans_list)+1) / max(len(user_ans_list), len(correct_ans_list)+1))
    score = max(score, 0)
    return score
 
 
def count_sandbox_score(user_id):
    user_ans_list = get_user_answers(user_id)
    correct_ans = get_correct_ans(user_id)
    best_solve_list = [6, 11, 15, 18, 20]
    correct_ans_list = []
    for _ in best_solve_list:
        if correct_ans < _:
            if correct_ans_list:
                correct_ans_list.append(_)
                correct_ans_list.extend(range(correct_ans_list[-2]+1, correct_ans+1))
            else:
                correct_ans_list = [6]
                correct_ans_list.extend(range(1, correct_ans+1))
            break
        elif correct_ans == _:
            correct_ans_list.append(_)
            break
        correct_ans_list.append(_)
 
    score = int(1000 * min(len(user_ans_list), len(correct_ans_list)+1) / max(len(user_ans_list), len(correct_ans_list)+1))
    return score
 
 
def check_if_broke(user_ans, correct_ans):
    try:
        if user_ans > correct_ans:
            return 1
        else:
            return 0
    except TypeError:
        return
 
 
def print_top(user_id):
    top = get_top_users()
    ret_str = f'{"place":>5}{"user id":>18}{"score":>9}'
    f = 1
    user_ind = 0
    for i in range(len(top)):
        if i < 5:
            if top[i][0] == user_id:
                f = 0
                ret_str += f'\n{i+1:>5}{user_id:>18}{get_user_best_score(user_id):>9}{"Это вы":>10}'
            else:
                ret_str += f'\n{i+1:>5}{top[i][0]:>18}{get_user_best_score(top[i][0]):>9}'
        else:
            if top[i][0] == user_id:
                user_ind = i
                break
    if f:
        ret_str += f'\n{user_ind+1:>5}{user_id:>18}{get_user_best_score(user_id):>9}{"Это вы":>10}'
    return ret_str