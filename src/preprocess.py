def get_food_and_price_list(receipt_raw: str):
    # append sentinel
    receipt = receipt_raw + '!'

    food_and_price = []
    food = ""
    price = ""

    # if receipt[i] is enclosed in parentheses
    is_Parentheses = False

    # if receipt[i] is part of the food name
    is_food = True

    # is the number a discount or a price
    is_discount = False

    for i in range(len(receipt)):
        # Exclude strings enclosed in parentheses
        if receipt[i] == '(':
            is_Parentheses = True
        if receipt[i] == ')':
            is_Parentheses = False
        if is_Parentheses and (not is_food):
            continue

        if receipt[i] not in ['¥', '-']:
            if is_food:
                food += receipt[i]
            else :
                # if receipt[i] is number
                if ord('0') <= ord(receipt[i]) <= ord('9'):
                    price += receipt[i]

                # if receipt[i] is not number
                else:
                    # if discount
                    if is_discount :
                        food_and_price[-1][1] -= int(price)
                    else:
                        food_and_price.append([food, int(price)])
                    is_food = True
                    food = receipt[i]
                    price = ""
        else:
            is_food = False
            is_discount = (receipt[i] == '-')

    return food_and_price

# [['みなとコーラゼロ500P', 155], ['ビッグアメリカンドッグ', 94], ['ツナ&コーンサラダ', 199], ['プレミアム焙煎ゴマドレッシング', 21]]