import pytest


def test_donation_exist_non_project(superuser_client, donation):
    response_donation = superuser_client.get('/donation/')
    data_donation = response_donation.json()
    assert len(data_donation) == 1, (
        'Если получено пожертвование, но открытых проектов нет, '
        'вся сумма из пожертвования должна ожидать открытия нового проекта.'
    )
    assert data_donation[0]['invested_amount'] == 0, (
        'Если получено пожертвование, но открытых проектов нет, '
        'сумма invested_amount должна оставаться нулевой.'
    )


def test_project_exist_non_donations(superuser_client, charity_project):
    response = superuser_client.get('/charity_project/')
    data = response.json()
    assert data[0]['invested_amount'] == 0, (
        'Если существует проект, но пожертвований пока нет, '
        'сумма invested_amount должна оставаться нулевой.'
    )


def test_fully_invested_amount_for_two_projects(user_client, charity_project, charity_project_nunchaku):
    """Создано 2 пустых проекта. Тест создает 2 пожертвования которые полностью покрывают инвестиции первого проекта. Второй проект должен оставаться не инвестированным."""
    user_client.post('/donation/', json={
        'full_amount': 500000,
    })
    user_client.post('/donation/', json={
        'full_amount': 500000,
    })
    print(charity_project)
    assert charity_project.fully_invested, test_fully_invested_amount_for_two_projects.__doc__
    assert not charity_project_nunchaku.fully_invested, test_fully_invested_amount_for_two_projects.__doc__
    assert charity_project_nunchaku.invested_amount == 0, test_fully_invested_amount_for_two_projects.__doc__


def test_donation_to_little_invest_project(user_client, charity_project_little_invested, charity_project_nunchaku):
    """Создано 2 проекта, один из которых частично инвестирован. Тест создает пожертвование. В первый проект пожертвования должны добавиться, а второй остатся не тронутым."""
    user_client.post('/donation/', json={
        'full_amount': 900,
    })
    assert not charity_project_little_invested.fully_invested, test_donation_to_little_invest_project.__doc__
    assert charity_project_little_invested.invested_amount == 1000, test_donation_to_little_invest_project.__doc__
    assert not charity_project_nunchaku.fully_invested, test_donation_to_little_invest_project.__doc__
    assert charity_project_nunchaku.invested_amount == 0, test_donation_to_little_invest_project.__doc__
