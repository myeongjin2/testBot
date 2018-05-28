# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.messages import Message
import pymysql


_host = "13.209.41.227"
_user = "root"
_db = "sample"
_password = "password"
        
db = pymysql.connect(host=_host, user=_user, db=_db, password=_password, charset='utf8')
cur = db.cursor(pymysql.cursors.DictCursor)

class Bot(BaseBot):
    # /start 시 출력
    def on_start(self, event, context):
        #menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
        content = event.get('content')  # 받은 메시지 Message에 저장
        
        if not content:
            if event['new_joined']:
                self.send_chatroom_welcome_message(event)
            return
        
        if content.startswith('/start'):
            self.send_welcome_message(event)
        
    
    def on_default(self, event, context):
        content = event.get('content')  # 받은 메시지 Message에 저장
        
        if content == '회의실 예약':
            self.reservation(event, context)
            return
            
        elif content == '예약 확인':
            self.confirm(event, content)
            return
        
        elif content =="예약 수정":
            self.modify(event, context)
            return
                
        elif content == "예약 취소":
            self.cancel(event, content)
            return        
        
        elif content == "예약 전체 목록":
            self.total_reservation(event, content)
            return
        
        else:
            recognized = self.recognize(event)            
            if recognized:
                return
        #self.send_error_message(event)
    
    def total_reservation(self, event, message):
        answer = self.get_project_data().get(message)
        msg = Message(event).set_text(answer.get('answer'))
        if answer.get('link'):
            msg.add_url_button(answer.get('title'), answer.get('link'))
            
        self.send_message(msg)
    
    '''
    def cancel(self, event, message):
        answer = self.get_project_data().get(message)
        msg = Message(event).set_text(answer.get('answer'))
        if answer.get('link'):
            msg.add_url_button(answer.get('title'), answer.get('link'))
            
        self.send_message(msg)

    
    def confirm(self, event, message):
        answer = self.get_project_data().get(message)
        msg = Message(event).set_text(answer.get('answer'))
        if answer.get('link'):
            msg.add_url_button(answer.get('title'), answer.get('link'))
            
        self.send_message(msg)
    

    def start_reservation_time(self, event):
        message = Message(event).set_text('시작 시간을 선택해주세요.')
        
        for i in range (9, 18):
            message.add_keyboard_button('%d:00' % i)
        
        self.send_message(message)
        self.end_reservation_time(self)
        
    def end_reservation_time(self, event):
        global nextStep
        
        tempStartTime = event['content']
        startTime = int(re.findall('\d+', tempStartTime)[0])
        nextStep = True
        message = Message(event).set_text('종료 시간을 선택해주세요.')
        
        for i in range (startTime + 1, 19):
            message.add_keyboard_button('%d:00' % i)
        
        self.send_message(message)
        
    def reservation_complete(self, event):
        menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
        message = Message(event).set_text('예약이 완료되었습니다.')
        
        for item in menu:
            message.add_keyboard_button(item)  # 키보드 버튼 생성
        self.send_message(message)
    '''
    def remember_chatroom(self, event):
        chat_id = event.get('chat_id')
        data = self.get_project_data()
        data['chat_id'] = chat_id
        self.set_project_data(data)
        
    def send_chatroom_welcome_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
        self.remember_chatroom(event)
        message = Message(event).set_text('안녕하세요? 회의실 예약 챗봇입니다.\n'\
                                          '무엇을 도와드릴까요?')
        for item in menu:
            message.add_keyboard_button(item)  # 키보드 버튼 생성
        
        self.send_message(message)
        
    def send_welcome_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
        message = Message(event).set_text('안녕하세요? 저는 회의실을 예약하는 챗봇입니다. ^_^\n무엇을 도와드릴까요?\n\n'\
                                          '1. 회의실 예약\n'\
                                          '2. 예약 확인\n'\
                                          '3. 예약 수정\n'\
                                          '4. 예약 취소')
        
        for item in menu:
            message.add_keyboard_button(item)  # 키보드 버튼 생성     
               
        self.send_message(message)
    
    def reservation(self, event, context):
        '''
        now_time = datetime.now() + timedelta(hours=9)  # 우리나라 시간으로 변경
        
        message = Message(event)
        message.set_text('What is the date of the meeting?\n(ex. 2018-05-05)')
        
        for i in range (1, 6):
            range_time = now_time + timedelta(days=i)
            str_range_time = range_time.strftime('%Y-%m-%d'.encode('unicode-escape').decode()).encode().decode('unicode-escape')
            message.add_keyboard_button(str_range_time)
        '''
        event['content']='/intent pool1'
        self.dispatcher.dispatch(event, context)
        
        #self.send_message(message)
    
    # /intent pools 가 정상적으로 완료되면 set_pools 함수로 intent에 저장된 값을 불러옴
    def set_pool1(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') # slots id 와 대응
            q2 = kwargs.get('question2')
            q3 = kwargs.get('question3')
            q4 = kwargs.get('question4')
            q5 = kwargs.get('question5')
            q6 = kwargs.get('question6')
            
            sql = "select * from `meeting` where meetingRoom = %s and date = %s "\
                    "and ((startTime < %s and endTime > %s) or (startTime < %s and endTime > %s) "\
                    "or (startTime >= %s and endTime <= %s) or (startTime <= %s and endTime >= %s))"
            
            cur.execute(sql, (q1, q4, q5, q5, q6, q6, q5, q6, q5, q6))
            rows = cur.fetchall()
            
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
            message = Message(event).set_text('예약에 실패했습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
            self.send_message(message)
            
        else:
            if(str(rows)=="()"):
                try:
                    sql = "insert into meeting(meetingRoom, subject, name, date, startTime, endTime)\
                                values(%s, %s, %s, %s, %s, %s)"  
                    cur.execute(sql, (q1,q2,q3,q4,q5,q6))
                    db.commit()
        
                except pymysql.InternalError:
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('예약에 실패했습니다.\n다시 한번 입력해주세요.')
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                    self.send_message(message)
            
                else:
                    sql = "select * from `meeting` order by id desc limit 1"
                    
                    cur.execute(sql)
                    rows = cur.fetchall()
            
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
            
                    for row in rows:
                        message = Message(event).set_text('\''+str(row['name'])+'\'님의 예약이 완료되었습니다.')
                        for item in menu:
                            message.add_keyboard_button(item)  # 키보드 버튼 생성   
                            #add_keyboard_button(item)  
               
                        self.send_message(message)
                
                    self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                      +'회의실: '+str(row['meetingRoom'])+'\n'\
                                      +'신청자: '+str(row['name'])+'\n'\
                                      +'회의 제목: '+str(row['subject'])+'\n'\
                                      +'회의 일자: '+str(row['date'])+'\n'\
                                      +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                      +'회의 종료 시간: '+str(row['endTime'])+'\n')
            else:
                menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                message = Message(event).set_text('\'' +q4 +' , ' +q5 +' ~ ' +q6 +'\' 는 이미 예약이 있습니다.\n'\
                                                  '다른 날짜를 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                self.send_message(message)
            
    def confirm(self, event, context):
        event['content']='/intent pool2'
        self.dispatcher.dispatch(event, context)
        
    # /intent pools 가 정상적으로 완료되면 set_pools 함수로 intent에 저장된 값을 불러옴
    def set_pool2(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1')
            q2 = kwargs.get('question2')
        
            sql = "select count(*) from meeting where name=%s and date=%s"
        
            cur.execute(sql, (q1, q2))
            rows = cur.fetchall()
            
        except pymysql.InternalError:
            menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
            message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
            self.send_message(message)
        else:
            if(str(rows)=="[{\'count(*)\': 0}]"):
                menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                message = Message(event).set_text('\''+q1+'\'님의 '+'\''+q2+'\' 예약 내역이 없습니다.')
                for item in menu:
                    message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                self.send_message(message)
            else:
                try:
                    sql = "select * from meeting where name=%s and date=%s"
                
                    cur.execute(sql, (q1, q2))
                    rows = cur.fetchall()
            
                except pymysql.InternalError:
                    '''
                    self.send_message('1234')
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성   
        
                    self.send_message(message)
                    '''
                else:
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('\''+q1+ '\'님의 '+'\'' +q2 +'\' 예약 내역입니다.')
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성
                        #add_keyboard_button(item)
               
                    self.send_message(message)
            
                    for row in rows:
                        self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                          +'회의실: '+str(row['meetingRoom'])+'\n'\
                                          +'신청자: '+str(row['name'])+'\n'\
                                          +'회의 제목: '+str(row['subject'])+'\n'\
                                          +'회의 일자: '+str(row['date'])+'\n'\
                                          +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                          +'회의 종료 시간: '+str(row['endTime'])+'\n')
            
    def modify(self, event, context):
        event['content']='/intent pool3'
        self.dispatcher.dispatch(event, context)
        
    # /intent pools 가 정상적으로 완료되면 set_pools 함수로 intent에 저장된 값을 불러옴
    def set_pool3(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') # slots id 와 대응
            q2 = kwargs.get('question2')
            q3 = kwargs.get('question3')
            q4 = kwargs.get('question4')
            q5 = kwargs.get('question5')
            q6 = kwargs.get('question6')
            q7 = kwargs.get('question7')
            
            sql = "select * from meeting where id=%s and name=%s"
            cur.execute(sql, (q2,q1))
            rows = cur.fetchall()
            
        except:
            '''
            menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
            message = Message(event).set_text('예약 수정에 실패했습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
            self.send_message(message)
            '''
        
        else:
            if(str(rows)=="()"):
                menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                message = Message(event).set_text('\''+q1+'\'님의 예약번호 '+'\'' +q2+'\'번 예약 내역이 없습니다.\n다시 한번 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                self.send_message(message)
            else:
                try:
                    sql = "update meeting set meetingRoom=%s, subject=%s, date=%s, startTime=%s, endTime=%s where id=%s and name=%s"
            
                    cur.execute(sql, (q3, q4, q5, q6, q7, q2, q1))
                    db.commit()
        
                except pymysql.InternalError:
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('예약 수정 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
                    
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                    self.send_message(message)
        
                else:
                    sql = "select * from meeting where id = %s"
                    cur.execute(sql, (q2))
                    rows = cur.fetchall()
            
                    for row in rows:
                        menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('\''+str(row['name'])+'\'님의 예약 수정이 완료되었습니다.')
                
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성     
               
                    self.send_message(message)

                    self.send_message('예약 번호: '+str(row['id'])+'\n'\
                                      +'회의실: '+str(row['meetingRoom'])+'\n'\
                                      +'신청자: '+str(row['name'])+'\n'\
                                      +'회의 제목: '+str(row['subject'])+'\n'\
                                      +'회의 일자: '+str(row['date'])+'\n'\
                                      +'회의 시작 시간: '+str(row['startTime'])+'\n'\
                                      +'회의 종료 시간: '+str(row['endTime'])+'\n')
            
    def cancel(self, event, context):
        event['content']='/intent pool4'
        self.dispatcher.dispatch(event, context)
        
    # /intent pools 가 정상적으로 완료되면 seㄷt_pools 함수로 intent에 저장된 값을 불러옴
    def set_pool4(self, event, context, **kwargs):
        try:
            q1 = kwargs.get('question1') # slots id 와 대응
            q2 = kwargs.get('question2')
            
            sql = "select * from meeting where name=%s and id=%s"
            
            cur.execute(sql, (q1,q2))
            rows = cur.fetchall()

        except:
            '''
            menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
            message = Message(event).set_text('예약 정보가 올바르지 않습니다.\n다시 한번 입력해주세요.')
            for item in menu:
                message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
            self.send_message(message)
            '''
        else:
            if(str(rows)=="()"):
                menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                message = Message(event).set_text('\''+q1+'\'님의 예약번호 '+'\'' +q2+'\'번 예약 내역이 없습니다.\n다시 한번 입력해주세요.')
                for item in menu:
                    message.add_keyboard_button(item)  # 키보드 버튼 생성   
               
                self.send_message(message)
            else:
                try:
                    sql = "delete from meeting where name=%s and id=%s"
            
                    cur.execute(sql, (q1, q2))
            
                    db.commit()
        
                except pymysql.InternalError:
                    self.send_message('오류가 발생했습니다.\n다시 시도해주세요.')
            
                else:
                    menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
                    message = Message(event).set_text('\''+q1+ '\'님의 예약번호 \'' +q2 +'\'번 예약이 취소되었습니다.')
        
                    for item in menu:
                        message.add_keyboard_button(item)  # 키보드 버튼 생성     
               
                    self.send_message(message)
                    
    def send_error_message(self, event):
        menu = self.get_project_data().get('set_menu').split(',')  # bothub Property 메뉴 생성
        message = Message(event).set_text('죄송합니다.\n'\
                                          '무슨 말씀인지 이해를 못했어요.\n다시 한번 입력해주세요.')
        for item in menu:
            message.add_keyboard_button(item)  # 키보드 버튼 생성
        self.send_message(message)

    def recognize(self, event):
        #global nextStep
        response = self.nlu('apiai').ask(event=event)
        action = response.action
        
        if action.intent == 'input.unknown':
            return False
        
        if not action.completed:
            self.send_message(response.next_message)
            return True
        
        if action.intent == 'reservation':
            self.reservation(event, '회의실 예약')
            return True
        
        if action.intent == 'confirm':
            self.confirm(event, '예약 확인')
            return True
        
        if action.intent == 'modify':
            self.modify(event, '예약 수정')
            return True
        
        if action.intent == 'cancel':
            self.cancel(event, '예약 취소')
            return True
        
        else:
            self.send_error_message(event)
            # self.send_message(response.next_message)
            return True