# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.messages import Message
import pymysql

#EC2 MySQL 정보
_host = "13.209.41.227" 
_user = "root"
_db = "sample"
_password = "password"

db = pymysql.connect(host=_host, user=_user, db=_db, password=_password, charset='utf8')
cur = db.cursor(pymysql.cursors.DictCursor)

class Bot(BaseBot):
    #/start 시 출력
    def on_start(self, event, context):
        content = event.get('content') #받은 메시지 Message에 저장
        
        if not content:
            if event['new_joined']: #User가 채팅방에 처음 입장했을 때
                self.send_chatroom_welcome_message(event)
            return
        
        if content.startswith('/start'): #User가 재방문 했을 때
            self.send_welcome_message(event)
        
    #User의 메시지를 받았을 때 시작되는 함수
    def on_default(self, event, context):        
        content = event.get('content') #받은 메시지 Message에 저장
        
        if content == '회의실 예약':
            self.reservation(event, context)
            return
        
        elif content == "날짜별 예약 현황":
            self.date_reservation(event, content)
            return
        
        elif content == '나의 예약 확인':
            self.confirm(event, content)
            return
        
        elif content =="날짜 수정":
            self.modify(event, context)
            return
        
        elif content == "예약 취소":
            self.cancel(event, content)
            return
        
        else:
            recognized = self.recognize(event) #api.ai 자연어 처리 API
            if recognized:
                return
    
    #채팅방에 처음 방문했을 때 발생하는 함수
    def send_chatroom_welcome_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
        self.remember_chatroom(event) #id를 저장하는 함수로 이동
        message = Message(event).set_text('처음뵙겠습니다. 저는 회의실을 예약하는 챗봇입니다. ^_^\n무엇을 도와드릴까요?\n\n'\
                                          '1. 회의실 예약\n'\
                                          '2. 날짜별 예약 현황\n'\
                                          '3. 나의 예약 확인\n'\
                                          '4. 날짜 수정\n'\
                                          '5. 예약 취소')
        for item in menu:
            message.add_keyboard_button(item) #키보드 버튼 생성
        
        self.send_message(message)
    
    #재방문시 기억하기 위해 id를 저장하는 함수
    def remember_chatroom(self, event):
        chat_id = event.get('chat_id')
        data = self.get_project_data()
        data['chat_id'] = chat_id
        self.set_project_data(data) #id를 bothub Properties에 저장
    
    #채팅방 재방문시 발생하는 함수
    def send_welcome_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
        message = Message(event).set_text('안녕하세요? 저는 회의실을 예약하는 챗봇입니다. ^-^\n무엇을 도와드릴까요?\n\n'\
                                          '1. 회의실 예약\n'\
                                          '2. 날짜별 예약 현황\n'\
                                          '3. 나의 예약 확인\n'\
                                          '4. 날짜 수정\n'\
                                          '5. 예약 취소')

        for item in menu:
            message.add_keyboard_button(item) #키보드 버튼 생성
               
        self.send_message(message)
    
    #에러 메시지 출력 함수
    def send_error_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
        message = Message(event).set_text('죄송합니다.ㅠ_ㅠ\n\
                                          무슨 말씀인지 이해를 못했어요.\n\
                                          다시 한번 입력해주세요.')
        for item in menu:
            message.add_keyboard_button(item) #키보드 버튼 생성
        self.send_message(message)
    
    #회의실 예약 함수
    def reservation(self, event, context):
        '''오늘 날짜를 불러오는 코드
        now_time = datetime.now() + timedelta(hours=9) #우리나라 시간으로 변경
        
        message = Message(event)
        message.set_text('What is the date of the meeting?\n(ex. 2018-05-05)')
        
        for i in range (1, 6):
            range_time = now_time + timedelta(days=i)
            str_range_time = range_time.strftime('%Y-%m-%d'.encode('unicode-escape').decode()).encode().decode('unicode-escape')
            message.add_keyboard_button(str_range_time)
        '''
        event['content']='/intent pool1' #dispatcher기능(bothub.yml 파일을 불러옴)
        self.dispatcher.dispatch(event, context)
    
    #/intent pools가 정상적으로 완료되면 set_pool 함수로 intent에 저장된 값을 불러옴
    def set_pool1(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') #slots id 와 대응
            q2 = kwargs.get('question2')
            q3 = kwargs.get('question3')
            q4 = kwargs.get('question4')
            q5 = kwargs.get('question5')
            q6 = kwargs.get('question6')
            
            #예약시 meetingRoom과 date가 중복되는지 확인하는 query
            sql = "select * from meeting where meetingRoom = %s and date = %s "\
                    "and ((startTime < %s and endTime > %s)"\
                    "or (startTime >= %s and endTime <= %s)"\
                    "or (startTime <= %s and endTime >= %s))"\
                    "or (startTime < %s and endTime > %s)"
            
            cur.execute(sql, (q1, q4, q5, q6, q5, q6, q5, q6, q5, q5))
        
        #각 column에 맞지 않는 데이터가 들어갔을 때
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
            
        else:
            if(str(rows)=="()"): #중복확인 query에서 중복되는 값이 안나왔을 때
                sql = "insert into meeting(meetingRoom, subject, name, date, startTime, endTime)\
                                    values(%s, %s, %s, %s, %s, %s)" #예약 정보를 insert하는 query
                cur.execute(sql, (q1,q2,q3,q4,q5,q6))
                db.commit()

                sql = "select * from meeting order by id desc limit 1" #가장 최근에 추가한 column 조회
                
                cur.execute(sql)
                rows = cur.fetchall()
        
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
        
                for row in rows:
                    message = Message(event).set_text('\''+str(row['name'])+'\'님의 예약이 완료되었습니다.')
                    for item in menu:
                        message.add_keyboard_button(item) #키보드 버튼 생성
           
                    self.send_message(message)

                self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                  +'회의실: '+str(row['meetingRoom'])+'\n'\
                                  +'신청자: '+str(row['name'])+'\n'\
                                  +'회의 제목: '+str(row['subject'])+'\n'\
                                  +'회의 일자: '+str(row['date'])+'\n'\
                                  +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                  +'회의 종료 시간: '+str(row['endTime'])+'\n')

            else: #중복확인 query에서 중복되는 값이 나왔을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\'' +q4 +' , ' +q5 +' ~ ' +q6 +'\' 는 이미 예약이 있습니다.\n'\
                                                  '다른 날짜를 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성

                self.send_message(message)
    
    #날짜별 예약 현황 함수
    def date_reservation(self, event, context):
        event['content']='/intent pool2'
        self.dispatcher.dispatch(event, context)
    
    def set_pool2(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1')
            
            sql = "select * from meeting where date=%s" #해당 날짜에 예약이 있는지 확인하는 query
        
            cur.execute(sql, (q1))
            rows = cur.fetchall()
        
        #각 column에 맞지 않는 데이터가 들어갔을 때
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('날짜가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
        else:
            if(str(rows)=="()"): #예약 확인 query에서 예약 내역이 없을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+q1+'\''+'은 예약 내역이 없습니다.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성
               
                self.send_message(message)
            else: #예약 확인 query에서 예약 내역이 있을 때
                sql = "select * from meeting where date=%s" #해당 날짜에 예약을 불러오는 query
            
                cur.execute(sql, (q1))
                rows = cur.fetchall()
                
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+q1+ '\'' +' 예약 내역입니다.') #해당 날짜 예약 내역 출력
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성

                self.send_message(message)
        
                for row in rows:
                    self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                      +'회의실: '+str(row['meetingRoom'])+'\n'\
                                      +'신청자: '+str(row['name'])+'\n'\
                                      +'회의 제목: '+str(row['subject'])+'\n'\
                                      +'회의 일자: '+str(row['date'])+'\n'\
                                      +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                      +'회의 종료 시간: '+str(row['endTime'])+'\n')
    
    #나의 예약 확인 함수
    def confirm(self, event, context):
        event['content']='/intent pool3'
        self.dispatcher.dispatch(event, context)
    
    def set_pool3(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1')
            q2 = kwargs.get('question2')
        
            sql = "select * from meeting where name=%s and date=%s" #예약 확인을 위해 이름과 날짜를 불러오는 query
        
            cur.execute(sql, (q1, q2))
            rows = cur.fetchall()
        
        #각 column에 맞지 않는 데이터가 들어갔을 때
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
        else:
            if(str(rows)=="()"): #해당 날짜에 이름과 일치하는 예약이 없을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+q1+'\'님의 '+'\''+q2+'\' 예약 내역이 없습니다.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성

                self.send_message(message)
            else: #해당 날짜에 이름과 일치하는 예약이 있을 때
                sql = "select * from meeting where name=%s and date=%s" #이름과 날짜를 불러오는 query
            
                cur.execute(sql, (q1, q2))
                rows = cur.fetchall()

                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+q1+ '\'님의 '+'\'' +q2 +'\' 예약 내역입니다.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성
           
                self.send_message(message)
        
                for row in rows:
                    self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                      +'회의실: '+str(row['meetingRoom'])+'\n'\
                                      +'신청자: '+str(row['name'])+'\n'\
                                      +'회의 제목: '+str(row['subject'])+'\n'\
                                      +'회의 일자: '+str(row['date'])+'\n'\
                                      +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                      +'회의 종료 시간: '+str(row['endTime'])+'\n')
    
    #날짜 수정 함수
    def modify(self, event, context):
        event['content']='/intent pool4'
        self.dispatcher.dispatch(event, context)

    def set_pool4(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') #slots id 와 대응
            q2 = kwargs.get('question2')
            
            sql = "select * from meeting where id=%s and name=%s" #예약번호와 이름이 일치하는지 확인하는 query
            
            cur.execute(sql, (q2,q1))
            rows = cur.fetchall()
            
            for row in rows:
                global meetingRoom2 #예약 정보를 set_pool7으로 넘겨주기 위해 global 변수 선언
                global id2
                global name2
                
                meetingRoom2 = row['meetingRoom']
                id2 = row['id']
                name2 = row['name']
            
        #각 column에 맞지 않는 데이터가 들어갔을 때
        except:
            '''
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('예약번호가 올바르지 않습니다.\n다시 한번 입력해주세요.')
                    
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
            '''
        else:
            if(str(rows)=="()"): #예약번호와 이름이 일치하는 query가 없을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+q1+'\'님의 예약번호 '+'\'' +q2+'\'번 예약 내역이 없습니다.\n다시 한번 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성
               
                self.send_message(message)
                
            else: #중복확인 query에서 중복되는 값이 안나왔을 때
                self.modify_data(event, context)
    
    #날짜 수정 data input 함수
    def modify_data(self, event, context):
        event['content']='/intent pool5'
        self.dispatcher.dispatch(event, context)
                
    def set_pool5(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') #slots id 와 대응
            q2 = kwargs.get('question2')
            q3 = kwargs.get('question3')
            
            #예약 수정시 meetingRoom과 date가 중복되는지 확인하는 query
            sql = "select * from meeting where meetingRoom = %s and date = %s "\
                    "and ((startTime < %s and endTime > %s)"\
                    "or (startTime >= %s and endTime <= %s)"\
                    "or (startTime <= %s and endTime >= %s)"\
                    "or (startTime < %s and endTime > %s))"
            
            cur.execute(sql, (meetingRoom2, q1, q2, q3, q2, q3, q2, q3, q2, q2))
            rows = cur.fetchall()
            
        except:
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('날짜 수정 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')

            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
        
        else:
            if(str(rows)!="()"): #중복확인 query에서 중복되는 값이 나왔을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\'' +q1 +' , ' +q2 +' ~ ' +q3 +'\' 는 이미 예약이 있습니다.\n'\
                                                  '다른 날짜를 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성
               
                self.send_message(message)
            else: #중복확인 query에서 중복되는 값이 안나왔을 때
                sql = "update meeting set date=%s, startTime=%s, endTime=%s\
                        where id=%s and name=%s" #수정된 예약 정보를 update하는 query
        
                cur.execute(sql, (q1, q2, q3, id2, name2))
                db.commit() #update 적용
                
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\''+name2+'\'님의 날짜 수정이 완료되었습니다.')
                
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성

                self.send_message(message)

                sql = "select * from meeting where id = %s" #예약 정보를 불러오기 위한 select query
                cur.execute(sql, (id2))
                rows = cur.fetchall()
                
                for row in rows:
                    self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                      +'회의실: '+str(row['meetingRoom'])+'\n'\
                                      +'신청자: '+str(row['name'])+'\n'\
                                      +'회의 제목: '+str(row['subject'])+'\n'\
                                      +'회의 일자: '+str(row['date'])+'\n'\
                                      +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                      +'회의 종료 시간: '+str(row['endTime'])+'\n')
    
    #예약 취소 함수
    def cancel(self, event, context):
        event['content']='/intent pool6'
        self.dispatcher.dispatch(event, context)

    def set_pool6(self, event, context, **kwargs):
        q1 = kwargs.get('question1') #slots id 와 대응
        q2 = kwargs.get('question2')
        
        sql = "select * from meeting where name=%s and id=%s" #이름과 예약번호가 일치하는지 확인하는 query
        
        cur.execute(sql, (q1,q2))
        rows = cur.fetchall()
        
        if(str(rows)=="()"): #일치하는 query가 없을 때
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('\''+q1+'\'님의 예약번호 '+'\'' +q2+'\'번 예약 내역이 없습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
                
            self.send_message(message)
        else: #일치하는 query가 있을 때
            sql = "delete from meeting where name=%s and id=%s" #일치하는 이름과 회원번호를 지우는 query
    
            cur.execute(sql, (q1, q2))
            db.commit()
    
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('\''+q1+ '\'님의 예약번호 \'' +q2 +'\'번 예약이 취소되었습니다.')

            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
       
            self.send_message(message)
    
    #Dialogflow 자연어 처리 API를 불러오는 함수
    def recognize(self, event):
        response = self.nlu('apiai').ask(event=event) #api_key를 저장
        action = response.action
        
        if action.intent == 'input.unknown':
            return False
        
        if not action.completed:
            self.send_message(response.next_message)
            return True
        
        if action.intent == 'reservation': #dialogflow intent가 회의실 예약일 때
            self.reservation(event, '회의실 예약')
            return True
        
        if action.intent == 'date_reservation':
            self.date_reservation(event, '날짜별 예약 현황')
            return True
        
        if action.intent == 'confirm':
            self.confirm(event, '나의 예약 확인')
            return True
        
        if action.intent == 'modify':
            self.modify(event, '날짜 수정')
            return True
        
        if action.intent == 'cancel':
            self.cancel(event, '예약 취소')
            return True
        
        if action.intent == 'today_start_reservation':
            params = action.parameters #api.ai parameters 호출
            
            global date2 #api.ai parameters의 값을 global 변수 형태로 set_pool7함수로 전달
            date2 = params['date']
            global time2
            time2 = params['time']
            
            self.today_start_reservation(event, 'date startTime 예약')
            return True
        
        if action.intent == 'whole_reservation':
            self.whole_reservation(event, '예약 전체 목록')
            return True
        
        else: #모든 intent에도 속하지 않으면 에러메시지 출력
            self.send_error_message(event)
            return True
        
    def today_start_reservation(self, event, context):
        event['content']='/intent pool7'
        self.dispatcher.dispatch(event, context)
        
    #/intent pools가 정상적으로 완료되면 set_pool 함수로 intent에 저장된 값을 불러옴
    def set_pool7(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') #slots id 와 대응
            q2 = kwargs.get('question2')
            q3 = kwargs.get('question3')
            q4 = date2 #global 변수를 통해 전달받음
            q5 = time2
            q6 = kwargs.get('question6')
            
            #예약시 meetingRoom과 date가 중복되는지 확인하는 query
            sql = "select * from meeting where meetingRoom = %s and date = %s "\
                    "and ((startTime < %s and endTime > %s)"\
                    "or (startTime >= %s and endTime <= %s)"\
                    "or (startTime <= %s and endTime >= %s)"\
                    "or (startTime < %s and endTime > %s))"
            
            cur.execute(sql, (q1, q4, q5, q6, q5, q6, q5, q6, q5, q5))
            rows = cur.fetchall()
        
        #각 column에 맞지 않는 데이터가 들어갔을 때
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
            message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item) #키보드 버튼 생성
               
            self.send_message(message)
            
        else:
            if(str(rows)=="()"): #중복확인 query에서 중복되는 값이 안나왔을 때
                sql = "insert into meeting(meetingRoom, subject, name, date, startTime, endTime)\
                                    values(%s, %s, %s, %s, %s, %s)" #예약 정보를 insert하는 query
                cur.execute(sql, (q1,q2,q3,q4,q5,q6))
                db.commit()

                sql = "select * from meeting order by id desc limit 1" #가장 최근에 추가한 column 조회
                
                cur.execute(sql)
                rows = cur.fetchall()
        
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
        
                for row in rows:
                    message = Message(event).set_text('\''+str(row['name'])+'\'님의 예약이 완료되었습니다.')
                    for item in menu:
                        message.add_keyboard_button(item) #키보드 버튼 생성
           
                    self.send_message(message)

                self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                  +'회의실: '+str(row['meetingRoom'])+'\n'\
                                  +'신청자: '+str(row['name'])+'\n'\
                                  +'회의 제목: '+str(row['subject'])+'\n'\
                                  +'회의 일자: '+str(row['date'])+'\n'\
                                  +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                  +'회의 종료 시간: '+str(row['endTime'])+'\n')

            else: #중복확인 query에서 중복되는 값이 나왔을 때
                menu = self.get_project_data().get('set_menu').split(',') #bothub Properties 메뉴 생성
                message = Message(event).set_text('\'' +q4 +' , ' +q5 +' ~ ' +q6 +'\' 는 이미 예약이 있습니다.\n'\
                                                  '다른 날짜를 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item) #키보드 버튼 생성

                self.send_message(message)

    #예약 전체 목록 함수
    def whole_reservation(self, event, message):
        answer = self.get_project_data().get(message) #Properties에 저장된 message를 저장
        msg = Message(event).set_text(answer.get('answer'))
        if answer.get('link'): #Properties에 저장된 link를 불러옴
            msg.add_url_button(answer.get('title'), answer.get('link'))
            
        self.send_message(msg)

    '''예약 시간 키보드 버튼 출력 함수
    def start_reservation_time(self, event):
        message = Message(event).set_text('시작 시간을 선택해주세요.')
        
        for i in range (9, 18):
            message.add_keyboard_button('%d:00' % i)
        
        self.send_message(message)
        self.end_reservation_time(self)
    '''
        
    '''예약 종료 키보드 버튼 출력 함수
    def end_reservation_time(self, event):
        tempStartTime = event['content']
        startTime = int(re.findall('\d+', tempStartTime)[0])
        message = Message(event).set_text('종료 시간을 선택해주세요.')
        
        for i in range (startTime + 1, 19):
            message.add_keyboard_button('%d:00' % i)
        
        self.send_message(message)
    '''