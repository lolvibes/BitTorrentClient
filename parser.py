
def decoder(data,index): # index should point to next unread byte not parsed byte
    char=data[index:index+1]
    #for the integer
    if char==b'i':
        start=index+1
        end=data.index(b'e',index)
        return int(data[start:end]) , end+1

    # for the string

    elif  data[index:index+1].isdigit(): # first checking if the given index have digit
        colon=data.index(b':',index) # position of our colon
        length=int(data[index:colon])# deducting how many digits which are character,    are there through slicing
        start=colon +1 # starting one position after colon
        end=start+length #this gives us string size as we only wanna read character same as digits
        return data[start:end], end # returning our readed string and next unreded index

    # for list
    elif char==b'l':
        index+=1
        items=[]#as u have list in data u have to store in data
        while data[index:index + 1] != b'e':
            result, new_index=decoder(data,index)
            items.append(result) # each recursive function will give result according to index and if statements
            index=new_index # update the index with new value when the previous if statement executes
        return items,index+1 # now one of tuple elements is list

    # for dictionary
    elif char==b'd':
        item={}
        #for key parsing(b encoded rule key only string)
        index += 1
        while data[index:index+1] !=b'e':
            key, index=decoder(data,index)
            value,index=decoder(data,index)
            item[key]=value
        return item, index+1 # +1 necesarry cuz it point toward the last byte readed

def encoder(data):
    if isinstance(data, int):
        return b'i' + str(data).encode() +b'e'
    elif isinstance(data,bytes):
        return str(len(data)).encode() + b':' + data
    elif isinstance(data,list):
        result=b'l'
        for i in data:
            result+=encoder(i)
        return result + b'e'
    elif isinstance(data,dict):
        result=b'd'
        for key in sorted(data.keys()):
            result+=encoder(key)
            result+=encoder(data[key])
        return result + b'e'
