from database.models import async_session, User, User_Templates, User_Modes, Answers

from sqlalchemy import select, update, delete, insert

async def set_user(tg_id, user_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        if not user:
            session.add(User(tg_id=tg_id, user_name=user_name))
            await session.commit()


async def set_template(tg_user_id, template_name, template_text, template_rating, template_product,all_stars,all_products):
    async with async_session() as session:
        # Perform the query to get user templates
        result = await session.execute(
            select(User_Templates).where(
                User_Templates.tg_user_id == tg_user_id,
                User_Templates.template_rating == template_rating
            )
        )

        # Use scalars() to get the actual objects
        user_templates_list = result.scalars().all()  # This will return a list of User_Templates objects

        # Check if there are less than 3 templates
        if len(user_templates_list) < 3:
            # Add the new template
            session.add(User_Templates(
                tg_user_id=tg_user_id,
                template_name=template_name,
                template_text=template_text,
                template_rating=template_rating,
                template_product=template_product,
                all_stars = all_stars,
                all_products = all_products
            ))
            await session.commit()  # Commit the session
            return True  # Indicate that the template was added
        else:
            return False  # Indicate that the limit was exceeded

async def get_template(tg_user_id, template_rating, template_product):
    async with async_session() as session:
        result = await session.scalar(
            select(User_Templates.template_text).where(
                User_Templates.tg_user_id == tg_user_id,
                User_Templates.template_rating == template_rating,
                User_Templates.template_product == template_product
            )
        )
        return result

async def get_templates(tg_user_id):
    async with async_session() as session:
        result = await session.execute(
            select(User_Templates.id, User_Templates.template_name, User_Templates.template_text, User_Templates.template_rating, User_Templates.template_product).where(
                User_Templates.tg_user_id == tg_user_id
            )
        )
        # Преобразуем результат в список списков
        templates = [list(row) for row in result.all()]
        return templates

async def delete_template(id):
    async with async_session() as session:
        await session.execute(delete(User_Templates).where(User_Templates.id == id))
        await session.commit()  # Commit the session

async def modes(tg_user_id, mode_rating, mode):
    async with async_session() as session:
        user_mode = await session.scalar(select(User_Modes.tg_user_id).where(User_Modes.tg_user_id == tg_user_id,
                                                                             User_Modes.mode_rating==mode_rating))
        if not(user_mode):
            session.add(User_Modes(
                tg_user_id=tg_user_id,
                mode_rating = mode_rating,
                mode_auto = mode
            ))
        else:
            await session.execute(
                update(User_Modes)
                .where(User_Modes.tg_user_id == tg_user_id, User_Modes.mode_rating==mode_rating)
                .values(mode_rating=mode_rating, mode_auto=mode)
            )
        await session.commit()  # Фиксируем изменения


async def start_mode(tg_user_id):
    async with async_session() as session:
        # Check if user modes already exist
        user_modes = await session.scalars(
            select(User_Modes).where(User_Modes.tg_user_id == tg_user_id).order_by(User_Modes.mode_rating)
        )
        user_modes_list = user_modes.all()  # Await the result and then call .all()

        # If no modes exist, insert default values
        if not user_modes_list:  # Check if the list is empty
            for i in range(1, 6):
                await session.execute(insert(User_Modes).values(tg_user_id=tg_user_id, mode_rating=i, mode_auto=False))
            await session.commit()  # Commit after inserting

            # Re-fetch user modes after insertion
            user_modes = await session.scalars(
                select(User_Modes).where(User_Modes.tg_user_id == tg_user_id).order_by(User_Modes.mode_rating)
            )
            user_modes_list = user_modes.all()  # Await the result and then call .all()

        # Prepare the result as a list of dictionaries
        res = [{"id": row.id, "tg_user_id": row.tg_user_id, "mode_rating": row.mode_rating, "mode_auto": row.mode_auto} for row in user_modes_list]
        return res

async def user_groups(tg_id, group):
    async with async_session() as session:

        await session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(user_group=group)
            )
        await session.commit()  # Commit the update

async def get_modes(tg_user_id):
    async with async_session() as session:
        all_modes = await session.scalars(select(User_Modes).where(User_Modes.tg_user_id==tg_user_id))
        all_modes_list = all_modes.all()
        res = [{'mode_rating': row.mode_rating, 'mode_auto': row.mode_auto} for row in all_modes_list]
        return res

async def add_answer(review_id, answer):
    async with async_session() as session:
        answer_value = await session.scalar(select(Answers.answer).where(Answers.review_id==review_id))
        if not (answer_value):
            session.add(Answers(
                review_id = review_id,
                answer = answer
            ))
        else:
            await session.execute(
                update(Answers)
                .where(Answers.review_id == review_id)
                .values(review_id = review_id, answer = answer)
            )
        await session.commit()  # Фиксируем изменения
async def get_answer(review_id):
    async with async_session() as session:
        answer = await session.scalar(
            select(Answers.answer).where(
                Answers.review_id==review_id
            )
        )
        return answer

async def delete_answer(review_id):
    async with async_session() as session:
        await session.execute(delete(Answers).where(Answers.review_id==review_id))
        await session.commit()  # Commit the session