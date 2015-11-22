from pymongo import MongoClient
from django.http import HttpResponse
from bson.json_util import dumps
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

def login_token():
  d = str(datetime.now())
  return hashlib.sha1(d).hexdigest()[0:32]

def hash_password(password):
  hash = password
  for i in range(0,16):
    hash = hashlib.sha1(hash).hexdigest()
  return hash

def next_index(l):
  index = 0
  length = len(l)
  if length == 0: return index
  indexes = [x['index'] for x in l]
  while True:
    if not(index in indexes):
      return index
    index+=1
    if index > 99:
      return -1

def get_conversation(l, w):
  for convo in l:
    if convo['with'] == w:
      return convo

def minus_index(l, index):
  result = []
  for listing in l:
    if not(str(listing['index']) == str(index)):
      result.append(listing)
  return result

def update_conversation(l, w, update):
  result = []
  for convo in l:
    if not(convo['with'] == w):
      result.append(convo)
  result.append(update)
  return result

def remove_conversation(l, w):
  result = []
  for convo in l:
    if not(convo['with'] == w):
        result.append(convo)
  return result

def connect():
  client = MongoClient('localhost', 27017)
  return client['byebooks']

def resolve_id(request):
  db = connect()
  ids = request.GET['user_ids']
  ids = ids.split(',')
  names = []
  for user_id in ids:
    user_query = {'user_id':user_id}
    user = db['users'].find_one(user_query)
    try:
      names.append(user['name'])
    except:
      pass
  names = [x for x in names if len(x) > 1]
  return HttpResponse(json.dumps(names), content_type="application/json")

def authenticate(request):
  password = request.POST['password']
  user_query = {'user_id':request.POST['user_id']}
  hash = hash_password(password)
  db = connect()
  user = db['users'].find_one(user_query)
  if hash == user['password']:
    user['token'] = login_token()
    db['users'].update(user_query, user)
    response = {'status':200, 'token':user['token']}
    return HttpResponse(json.dumps(response), content_type='application/json')
  return HttpResponse('Invalid')

def endpoint_search(request):
  query = {}
  get = request.GET
  if 'isbn' in get: query['isbn'] = get['isbn']  
  if 'title' in get: query['title'] = get['title']  
  if 'author' in get: query['author'] = get['author']  
  if 'edition' in get: query['edition'] = get['edition']  
  campus = get['campus']
  users_query = {'campus':campus}
  db = connect()
  users = db['users'].find(users_query)
  matches = []
  for user in users:
    for listing in user['storefront']:
      for key in get.keys():
        try:
          if listing[key] == query[key]:
            if not(key == 'campus'):
              matches.append({'user_id':user['user_id'],'listing':listing})
              break
        except:
          pass
  return HttpResponse(json.dumps(matches),content_type="application/json")

def endpoint_remove_conversation(request):
  db = connect()
  user_query = {'user_id':request.POST['user_id']}
  user = db['users'].find_one(user_query)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  other_user_id = request.POST['with']
  user['conversations'] = remove_conversation(user['conversations'],other_user_id)
  db['users'].update(user_query, user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')  

def send_message(request):
  msg = {}
  msg['from'] = request.POST['from']
  msg['data'] = request.POST['data']
  user_query = {'user_id':msg['from']}
  other_user_query = {'user_id':request.POST['to']}
  db = connect()
  user = db['users'].find_one(user_query)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  other_user = db['users'].find_one(other_user_query)
  conversations = user['conversations']
  other_users = [x['with'] for x in conversations]
  if not(other_user['user_id'] in other_users):
    conversations.append({'with':other_user['user_id'],'content':[],'unread':0})
  conversation = get_conversation(conversations, other_user['user_id'])
  conversation['content'].append(msg)
  user['conversations'] = update_conversation(conversations, conversation['with'],conversation)
  db['users'].update(user_query, user)
  # in the context of the "other" user from this point forward
  conversations = other_user['conversations']
  other_users = [x['with'] for x in conversations]
  if not(user['user_id'] in other_users):
    conversations.append({'with':user['user_id'],'content':[],'unread':1})
  conversation = get_conversation(conversations, user['user_id'])
  conversation['content'].append(msg)
  other_user['conversations'] = update_conversation(conversations, conversation['with'],conversation)
  db['users'].update(other_user_query, other_user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')  

def remove_wishlist(request):
  user = {'user_id': request.POST['user_id']}
  index = request.POST['index']
  db = connect()
  user_query = user
  user = db['users'].find_one(user)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  user['wishlist'] = minus_index(user['wishlist'],index)
  db['users'].update(user_query,user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')

def remove_storefront(request):
  user = {'user_id': request.POST['user_id']}
  index = request.POST['index']
  db = connect()
  user_query = user
  user = db['users'].find_one(user)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  user['storefront'] = minus_index(user['storefront'],index)
  db['users'].update(user_query,user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')

def get_user(request):
  try:
    query = {'user_id': request.GET['user_id']}
  except:
    return HttpResponse('Error')
  db = connect()
  users = db['users']
  user = users.find_one(query)
  return HttpResponse(dumps(user), content_type='application/json')  

def append_wishlist(request):
  wish = {}
  user = {'user_id': request.POST['user_id']}
  wish['isbn'] = request.POST['isbn']
  wish['title'] = request.POST['title']
  wish['edition'] = request.POST['edition']
  wish['author'] = request.POST['author']
  db = connect()
  user_query = user
  user = db['users'].find_one(user)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  wish['index'] = next_index(user['wishlist'])
  user['wishlist'].append(wish)
  db['users'].update(user_query,user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')

def append_storefront(request):
  sale = {}
  user = {'user_id': request.POST['user_id']}
  sale['isbn'] = request.POST['isbn']
  sale['title'] = request.POST['title']
  sale['edition'] = request.POST['edition']
  sale['author'] = request.POST['author']
  sale['price'] = request.POST['price']
  sale['notes'] = request.POST['notes']
  db = connect()
  user_query = user
  user = db['users'].find_one(user)
  if not(request.POST['token'] == user['token']): return HttpResponse('Invalid')
  sale['index'] = next_index(user['storefront'])
  user['storefront'].append(sale)
  db['users'].update(user_query,user)
  response = {'status':200}
  return HttpResponse(json.dumps(response),content_type='application/json')

#function name conflict
def endpoint_get_conversation(request):
  user = {'user_id':request.GET['user_id']}
  db = connect()
  user = db['users'].find_one(user)
  if not(request.GET['token'] == user['token']): return HttpResponse('Invalid')
  conversations = user['conversations']
  conversation = get_conversation(conversations, request.GET['with'])
  return HttpResponse(json.dumps(conversation), content_type="application/json")


def get_conversations(request):
  user = {'user_id':request.GET['user_id']}
  db = connect()
  user = db['users'].find_one(user)
  if not(request.GET['token'] == user['token']): return HttpResponse('Invalid')
  return HttpResponse(json.dumps(user['conversations']), content_type="application/json")

def get_wishlist(request):
  user = {'user_id':request.GET['user_id']}
  db = connect()
  user = db['users'].find_one(user)
  return HttpResponse(json.dumps(user['wishlist']), content_type="application/json")

def get_storefront(request):
  user = {'user_id':request.GET['user_id']}
  db = connect()
  user = db['users'].find_one(user)
  return HttpResponse(json.dumps(user['storefront']), content_type="application/json")


def create_user(request):
  response = {}
  db = connect()
  user = {'user_id': request.POST['user_id']}
  user['name'] = request.POST['name']
  user['wishlist'] = []
  user['storefront'] = []
  user['conversations'] = []
  user['campus'] = request.POST['campus']
  user['token'] = login_token()
  user['password'] = hash_password(request.POST['password'])
  if db['users'].find_one({'user_id':user['user_id']}) == None:
    db['users'].insert(user)
  response = {'status':200, 'token':user['token'] }
  return HttpResponse(json.dumps(response), content_type='application/json')
