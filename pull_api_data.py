import requests


def convert_tuple_to_list(tuple_var):
    """
    Converts tuple to a list
    Note: This isn't really necessary, but accounts for 1D tuple cases so i'm using it
    """

    list_var = []

    # Need to process 1D and 2D tuples differently
    if type(tuple_var[0]) is tuple:
        for value in tuple_var:
            dict_key = value[0]
            dict_value = value[1]

            list_var.append([dict_key, dict_value])
    else:
        dict_key = tuple_var[0]
        dict_value = tuple_var[1]

        list_var.append([dict_key, dict_value])

    return list_var


def convert_dict_to_list(dict_var):
    """ Converts dictionary to a 2D list """

    list_var = []
    for param, param_value in dict_var.items():
        list_var.append([param, param_value])

    return list_var


def pull_data(season_id, league_id, params=None):
    """ Returns a JSON object containing the data pulled APIs url """

    if params == None:
        params = []

    if season_id < 2020:
        url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
              str(league_id) + "?seasonId=" + str(season_id)
    else:
        url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
              str(season_id) + "/segments/0/leagues/" + str(league_id)

    # Passing the dict_params directly to the request_params of the requests.get method was
    # resulting in certain pulls retrieving unspecified data.
    # So, I'm directly applying those parameters to the URL string to prevent this
    # Note: This was likely happening due to duplicate keys being used (e.g. "view") in the dict

    if type(params) is tuple:
        params = convert_tuple_to_list(params)

    if type(params) is dict:
        params = convert_dict_to_list(params)

    for full_param in params:
        param = str(full_param[0])
        param_value = str(full_param[1])

        if url.find("?") == -1:
            url = url + "?" + param + "=" + param_value
        else:
            url = url + "&" + param + "=" + param_value

    r = requests.get(url)

    if r.status_code == 200:
        pass
    else:
        if r.status_code == 429:
            print("429 error")

        return None

        # 2020 url returns JSON object while prior season_ids return it in a list
    if season_id < 2020:
        d = r.json()[0]
    else:
        d = r.json()

    r.close()

    return d