from flask import current_app, request
import json
import requests
from random import randint, sample
from . import main
from app.models import User, Post, PostRate
from app import fake


@main.route('/run_bot')
def run_bot():
    base_url = request.host_url
    users = []
    errors = []
    for i in range(current_app.config['MAX_USERS_SIGNUP']):
        # sign up
        payload = {
            'email': fake.email(),
            'password': '111111'
        }
        headers = {'Content-Type': 'application/json'}

        res = requests.post('{}signup'.format(base_url), data=json.dumps(payload), headers=headers)
        json_data = res.json()
        if res.status_code == 200 and 'error' not in json_data:
            users.append({
                'id': json_data['id'],
                'email': payload['email'],
                'password': payload['password'],
            })
        elif 'error' in json_data:
            errors.append(json_data['error'])

    for user in users:
        # login user
        payload = {
            'email': user['email'],
            'password': user['password']
        }
        headers = {'Content-Type': 'application/json'}
        res = requests.post('{}login'.format(base_url), data=json.dumps(payload), headers=headers)
        json_data = res.json()
        if res.status_code == 200 and 'error' not in json_data:
            user['access_token'] = json_data['access_token']
            user['refresh_token'] = json_data['refresh_token']

            # create posts
            posts_to_create = randint(1, current_app.config['MAX_POSTS_PER_USER'])
            for k in range(posts_to_create):
                payload = {'body': fake.text()}
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer {}'.format(user['access_token'])
                }
                res = requests.post('{}posts'.format(base_url), data=json.dumps(payload), headers=headers)
                json_data = res.json()
                if 'error' in json_data:
                    errors.append(json_data['error'])
        elif 'error' in json_data:
            errors.append(json_data['error'])

    # rate posts
    all_posts = Post.all()
    for user in users:
        num_posts_to_rate = randint(1, current_app.config['MAX_LIKES_PER_USER'])
        if len(all_posts) > num_posts_to_rate:
            posts = sample(all_posts, k=num_posts_to_rate)
        else:
            posts = all_posts
        for p in posts:
            post = Post.get(p['id'])
            if post is None:
                errors.append('Post not found, ID {}'.format(p['id']))
                continue
            if post.check_author(user['id']):
                continue
            payload = {
                'post_id': post.id,
                'is_like': randint(0, 1)
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(user['access_token'])
            }
            res = requests.post('{}posts/rate'.format(base_url), data=json.dumps(payload), headers=headers)
            json_data = res.json()
            if 'error' in json_data:
                errors.append(json_data['error'])

    return {
        'errors': errors,
        'user_stats': User.stats(),
        'top_ten_posts': PostRate.get_posts_rating()
    }
