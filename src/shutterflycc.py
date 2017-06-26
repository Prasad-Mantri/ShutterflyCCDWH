from dateutil import rrule
from dateutil.parser import parse
from operator import itemgetter


# Function to ingest data into D
def ingest(e, D):
    #converting string into Dictionary to access the keys and values from it
    data_dct = eval(e)
    #find customer key from the event
    if data_dct['type']== 'CUSTOMER':
        cust_key = data_dct['key']
    else:
        cust_key = data_dct['customer_id']

  #  parsing the time using parser facility
    if 'event_time' in data_dct:
            data_dct['event_time'] = parse(data_dct['event_time'])

  # Adding customer in main dictionary
    if cust_key in D:
        D[cust_key].append(data_dct)
    else:
        D[cust_key] = [data_dct]



#Function to read all the events from input file one by one and ingest them in Data D
def read_events(D):
    #reading the events input file
    inp_file = open("Input.txt")
    countr = 0;
    # removing extra characters from event string
    # keeping the counter to remove extra punctuations from first event string and
    # other punctuations for the rest of the strings
    for each_event in inp_file:
        if countr==0:
            each_event = each_event.strip()[1:-1]
        else:
            each_event = each_event.strip()[:-1]
        ingest(each_event, D)
        countr = countr+1

#get Top X customers with Simple LTV Value
def TopXSimpleLTVCustomers(x, D):

    #After considering the FAQ question regarding the visits information, visits Calculations are kept for business
    # purposes and the final_amount is directly used in calculation Simple LTV.
    # Used final_amount in LTV calculation.
    list_topXSimpleLTVCustomers =[]
    cust_site_visits=[]

    for cust_key in D:
        #adding all site visit event times in list
        for ev in D[cust_key]:
          if ev['type'] == 'SITE_VISIT':
              cust_site_visits.append(ev['event_time'])
        #print cust_site_visits
        #checking if list of event times is not empty
        if not cust_site_visits:
            # adding 0 for the customers not having any order
            list_topXSimpleLTVCustomers.append((cust_key, 0))
        else:
            #checking if customer placed order
            if check_order(cust_key,D):
                #calculating number of weeks from list of event times
                total_weeks = rrule.rrule(rrule.WEEKLY, dtstart=min(cust_site_visits), until=max(cust_site_visits))
                total_num_visits = len(cust_site_visits)

                #calculating average visits per week for customer
               # avrg_visits_per_week = (float)(total_num_visits / total_weeks.count())

                #getting order list from given Data D
                order_details_list = order_details(cust_key,D)

                #creating amount list with each order and updating it if already present
                cust_order_amnt = {}
                for key,verb,event_time,total_amount in order_details_list:
                    if key in cust_order_amnt:
                        if event_time > cust_order_amnt[key][0]:
                            cust_order_amnt[key] = (event_time,total_amount)
                    else:
                        cust_order_amnt[key] = (event_time,total_amount)

                #Aggreagating all the amounts in list to get the final amount
                final_amount=0
                for key in cust_order_amnt:
                    final_amount = final_amount + cust_order_amnt[key][1]

          #Keeping the calculations using no of visits under the comments
          # calculating expenditures by customer per visit as per given requirement.
              #  avrg_exp_per_visit = final_amount /  avrg_visits_per_week
          # calculating customer value per week as per given requirement
              #  cust_value_per_week = avrg_exp_per_visit * avrg_visits_per_week

                simple_lifetime_value = 52 * final_amount * 10 # Given Average Shutterfly lifespan = 10.
                list_topXSimpleLTVCustomers.append((cust_key,simple_lifetime_value))


    list_topXSimpleLTVCustomers.sort(key=itemgetter(1), reverse= True)
    return list_topXSimpleLTVCustomers[:x]


def check_order(cust_key,D):
    for ev in D[cust_key]:
        if ev['type']=='ORDER':
            return True

def order_details(cust_key,D):
    order_details_list =[]
    for ev in D[cust_key]:
        if ev['type']=='ORDER':
            order_details_list.append((ev['key'],ev['verb'],ev['event_time'],float(ev['total_amount'].split()[0])))
    return order_details_list

def write_output_file(top_ltv_customers):
    out_file = open("Output.txt","w")
    out_file.write("Customer_ID, SimpleLTV_Value"+ '\n')
    for rec in top_ltv_customers:
        out_file.write(rec[0] + ', ' + str(rec[1]) + '\n')
    out_file.close()


if __name__ == '__main__':
    input_data = {}
    read_events(input_data)
    top_ltv_customers = TopXSimpleLTVCustomers(10,input_data)
    write_output_file(top_ltv_customers)
    print "Output file has been created with Top LTV Customers"
