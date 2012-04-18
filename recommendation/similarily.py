# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'

from math import sqrt, pow

def euclid(item_a, item_b):
    '''
        simple complete euclid distance
        '''
    item_a_likes, item_b_likes = __get_same(item_a, item_b)

    sum_pow = 0
    for i in len(item_a_likes):
        sum_pow += pow(item_a_likes[i].score - item_b_likes[i].score)

    return 1/ 1 + sqrt(sum_pow)

def pearson(item_a, item_b):
    '''
        pearson algorithm of distance
        list_a is User A likes tags
        list_b is User B likes tags
        only calculate the same one
        the more ,see algorithm,
        http://baike.baidu.com/albums/779030/779030/0/0.html#0$d0526df02bf26bbca50f5220
        '''

    item_a_likes, item_b_likes = __get_same(item_a, item_b)

    num = len(item_a_likes)
    if num == 0:
        return 1

    sum1 = sum([item_a_likes[i].socre for i in range(num)])
    sum2 = sum([item_b_likes[i].socre for i in range(num)])

    sum1_sq = sum([pow(item_a_likes[i].score, 2) for i in range(num)])
    sum2_sq = sum([pow(item_b_likes[i].score, 2) for i in range(num)])

    p_sum = sum([(item_a_likes[i].score*item_b_likes[i].score) for i in range(num)])

    mol = p_sum - sum1*sum2/num
    den = sqrt(sum1_sq - pow(sum1, 2)/num)*(sum2_sq - pow(sum2, 2)/num)

    if den == 0:
        return 0

    return mol/den

def __get_same(item_a, item_b):
    item_a_likes = []
    item_b_likes = []
    tmp = [b.item_id for b in item_b.likes]
    for like in item_a.likes:
        if like.item_id in tmp:
            item_a_likes.append(like)
            item_b_likes.append(like)

    return item_a_likes, item_b_likes

