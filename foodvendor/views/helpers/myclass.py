from ...serializers import NotificationSerializer

class Notification:
    def __init__(self,vendor,message,message_status,cust_list=[]):
        self.vendor = vendor
        self.message = message
        self.message_status = message_status
        self.cust_list = cust_list

    # def push_notification(self):
    #     details ={
    #     "vendor":self.vendor,
    #     "customer" : self.cust_list,
    #     "message_id" : self.message_id,
    #     "order_id" : self.order_id,
    #     "order_status_id" : self.order_status_id
    #     }
    #     serializer  = NotificationSerializer(data=details)
    #     if serializer.is_valid():
    #         serializer.save()

    def push_notification_to_all(self):
        all_customers = self.cust_list
        for customer in all_customers:
            details ={
            "vendor":self.vendor,
            "customer" : customer,
            "message" : self.message,
            "message_status" : self.message_status
            }
            serializer  = NotificationSerializer(data=details)
            print(details)
            if serializer.is_valid():
                serializer.save()