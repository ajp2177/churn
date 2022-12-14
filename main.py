import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sea
import matplotlib as plt
#import yaml
from matplotlib.figure import Figure
from PIL import Image
from sklearn.feature_extraction import DictVectorizer
import pickle
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split


import pandas_profiling

from streamlit_pandas_profiling import st_profile_report


#import streamlit_authenticator as stauth
#from yaml import SafeLoader


import json

import requests

df = pd.read_csv('/Users/andrewpullar/Downloads/WA_Fn-UseC_-Telco-Customer-Churn.csv')

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(0)

df.columns = df.columns.str.lower().str.replace(' ', '_')

string_columns = list(df.dtypes[df.dtypes == 'object'].index)

for col in string_columns:
    df[col] = df[col].str.lower().str.replace(' ', '_')

df.churn = (df.churn == 'yes').astype(int)


df.head()


df_train_full, df_test = train_test_split(df, test_size=0.2, random_state=1)
df_train, df_val = train_test_split(df_train_full, test_size=0.33, random_state=11)

y_train = df_train.churn.values
y_val = df_val.churn.values

del df_train['churn']
del df_val['churn']


categorical = ['gender', 'seniorcitizen', 'partner', 'dependents',
               'phoneservice', 'multiplelines', 'internetservice',
               'onlinesecurity', 'onlinebackup', 'deviceprotection',
               'techsupport', 'streamingtv', 'streamingmovies',
               'contract', 'paperlessbilling', 'paymentmethod']
numerical = ['tenure', 'monthlycharges', 'totalcharges']


train_dict = df_train[categorical + numerical].to_dict(orient='records')

dv = DictVectorizer(sparse=False)
dv.fit(train_dict)

X_train = dv.transform(train_dict)


model = LogisticRegression(solver = 'liblinear', random_state=1)
model.fit(X_train, y_train)

pickle.dump(model, open('churn_clf.pkl', 'wb'))


val_dict = df_val[categorical + numerical].to_dict(orient='records')
X_val = dv.transform(val_dict)
y_pred = model.predict_proba(X_val)[:, 1]

small_subset = ['contract', 'tenure', 'totalcharges']
train_dict_small = df_train[small_subset].to_dict(orient='records')
dv_small = DictVectorizer(sparse=False)
dv_small.fit(train_dict_small)

X_small_train = dv_small.transform(train_dict_small)

model_small = LogisticRegression(solver='liblinear', random_state=1)
model_small.fit(X_small_train, y_train)


val_dict_small = df_val[small_subset].to_dict(orient='records')
X_small_val = dv_small.transform(val_dict_small)

y_pred_small = model_small.predict_proba(X_small_val)[:, 1]


y_pred = model.predict_proba(X_val)[:, 1]
churn = y_pred >= 0.5
(churn == y_val).mean()


dict(zip(dv.get_feature_names(), model.coef_[0].round(3)))


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.subheader("**Enter password to access Churn prediction application**")
        st.text_input(
            "Password:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("Incorrect password, please try again.")
        return False
    else:
        # Password correct.
        return True


if check_password():
    #st.sidebar.info('This app is created to predict Customer Churn')
    churn = pd.read_csv('/Users/andrewpullar/Downloads/Telco_customer_churn.csv')
    activities = ["Home", "Exploratory Data Analysis", "Data Cleaning", "Modeling"]
    info = '''Select one of the options in the dropdown list to access specific page'''
    choice = st.sidebar.selectbox("Choose a page: ",activities, help = info)
    listo = ['Page Description', 'How to access different pages', 'About app']
    text = '''Click the help button to answer questions about page'''
    help = st.sidebar.button("Help", help=text)
#st.sidebar.success("Select a page from the drop-down menu.")
    if choice == "Home":
            st.image("https://images.squarespace-cdn.com/content/v1/"
                 "588f9607bebafbc786f8c5f8/1607924812500-Y1JR8L6XP5NKF2YPHDUX/image6.png", use_column_width=True)
            st.markdown("<h1 style='text-align: center; color: black;'>"
                        "Welcome! To access different pages of the application "
                        "and predict customer churn, use the dropdown list on the left-hand side of "
                        "the page.</h1>", unsafe_allow_html=True)
            st.sidebar.image("/Users/andrewpullar/Downloads/home-page.png", width=100)
        
            learn =  st.sidebar.selectbox("What would you like to learn more about?", listo)
            if learn == "Page Description":
                st.sidebar.markdown("This is the home page of the Churn prediction application")
            elif learn == "How to access different pages":
                st.sidebar.markdown("To access a different page, select a page from the dropdown list titled 'Choose a page' above.")
            elif learn == "About app":
                st.sidebar.markdown("This application provides detailed pages covering exploratory data analysis, data cleaning and modeling to help predict whether a customer will churn or not")


    elif choice == 'Exploratory Data Analysis':
            st.title("Exploratory Data Analysis")
            tab1, tab2 = st.tabs(["Intial Exploratory Analysis", "Plots"])

            churn.loc[(churn['Total Charges'] == ' '), 'Total Charges'] = 0
            churn['Total Charges'] = pd.to_numeric(churn['Total Charges'])
            with tab1:
                col1, col2, col3 = st.columns(3)
                col3.metric("Churn Rate", "27%")
                col1.metric("Number of Customers", "7,043")
                col2.metric("Churned Customers", "1,869")
                option = st.selectbox(
                    'Which EDA feature would you like to explore?',
                    ('View telco dataset', 'Generate profile report','Descriptive statistics'))

                if option == "View telco dataset":
                    dataframe = st.dataframe(churn)

                    @st.experimental_memo
                    def convert_df(churn):
                        return churn.to_csv(index=False).encode('utf-8')


                    csv = convert_df(churn)

                    st.download_button(
                        "Download telco dataset",
                        csv,
                        "file.csv",
                        "text/csv",
                        key='download-csv'
                    )

                    code = '''#load data
    churn = pd.read_csv('/Users/andrewpullar/Downloads/Telco_customer_churn.csv')
    churn.head(5)'''
                    st.markdown("**Code:**")
                    st.code(code, language='python')
                elif option == "Generate profile report":
                    pr = churn.profile_report()
                    st_profile_report(pr)
                    save = st.button("Save report")
                    if save:
                        pr.to_file("Analysis.html")

                elif option == "Descriptive statistics":
                    st.write(churn.describe())
                    st.markdown("**Code:**")
                    code = '''churn.describe()'''
                    st.code(code, language='python')

            with tab2:
                st.sidebar.image("https://miro.medium.com/max/1200/1*PKXC0FeXQc5LVmqhJ8HnVg.png", width=125)
                sc = st.selectbox("Select type of plots to visualize: ", ('Customer churn overview',
                                                                     'Demographic',
                                                                     "Customer services",
                                                                     "Customer account info"))
                st.markdown("_Use expanding arrows in upper-right corner next to plot to view them fullscreen_")

                if sc == "Customer churn overview":
                    st.markdown('**Customer Churn**')
                    st.image("/Users/andrewpullar/Desktop/churntotals.png")
                    with open("/Users/andrewpullar/Desktop/churntotals.png", "rb") as file:
                        btn = st.download_button(
                            label="Download image",
                            data=file,
                            file_name="churntotals.png",
                            mime="image/png"
                        )
                    code = '''sea.countplot(x = churn['Churn Label'])
    mplt.title('Churn')
    mplt.show()'''
                    st.markdown("**Code:**")
                    st.code(code, language='python')

                    st.markdown("**Percentage of each churn label**")
                    plot2 = px.pie(churn, names='Churn Label')
                    st.plotly_chart(plot2)


                    st.markdown('**Top 10 reasons for Customer Churn**')
                    st.image("/Users/andrewpullar/Downloads/churnreasons.png")
                    with open("/Users/andrewpullar/Downloads/churnreasons.png", "rb") as file:
                        btn = st.download_button(
                            label="Download image",
                            data=file,
                            file_name="churnreasons.png",
                            mime="image/png"
                        )
                    code = '''churn['Churn Reason'].value_counts()[:10].plot(kind='barh')'''
                    st.markdown("**Code:**")
                    st.code(code, language='python')


                elif sc == "Demographic":
                        fig2 = Figure()
                        fig2.set_size_inches(10, 8, forward=True)
                        axes = fig2.subplots(nrows=2, ncols=2)

                        sea.countplot(x="Gender", hue="Churn Label", data=churn, ax=axes[0, 0])
                        sea.countplot(x="Senior Citizen", hue="Churn Label", data=churn, ax=axes[0, 1])
                        sea.countplot(x="Partner", hue="Churn Label", data=churn, ax=axes[1, 0])
                        sea.countplot(x="Dependents", hue="Churn Label", data=churn, ax=axes[1, 1])
                        st.pyplot(fig2)


                elif sc == "Customer services":
                    fig3 = Figure()
                    fig3.set_size_inches(12, 14, forward=True)
                    axes = fig3.subplots(nrows=3, ncols=3)

                    sea.countplot(x="Phone Service", hue="Churn Label", data=churn, ax=axes[0, 0])
                    sea.countplot(x="Multiple Lines", hue="Churn Label", data=churn, ax=axes[0, 1])
                    sea.countplot(x="Internet Service", hue="Churn Label", data=churn, ax=axes[0, 2])
                    sea.countplot(x="Online Security", hue="Churn Label", data=churn, ax=axes[1, 0])
                    sea.countplot(x="Online Backup", hue="Churn Label", data=churn, ax=axes[1, 1])
                    sea.countplot(x="Device Protection", hue="Churn Label", data=churn, ax=axes[1, 2])
                    sea.countplot(x="Tech Support", hue="Churn Label", data=churn, ax=axes[2, 0])
                    sea.countplot(x="Streaming TV", hue="Churn Label", data=churn, ax=axes[2, 1])
                    sea.countplot(x="Streaming Movies", hue="Churn Label", data=churn, ax=axes[2, 2])
                    st.pyplot(fig3)

                elif sc == "Customer account info":
                    fig4 = Figure()
                    fig4.set_size_inches(12, 8, forward=True)
                    axes = fig4.subplots(nrows=1, ncols=3)

                    sea.countplot(x="Contract", hue="Churn Label", data=churn, ax=axes[0])
                    sea.countplot(x="Paperless Billing", hue="Churn Label", data=churn, ax=axes[1])
                    sea.countplot(x="Payment Method", hue="Churn Label", data=churn, ax=axes[2])
                    axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=45, ha="right")
                    st.pyplot(fig4)

                    st.markdown('**Customer Churn based on tenure and monthly charges**')
                    st.image("/Users/andrewpullar/Desktop/four.png")
    elif choice == 'Data Cleaning':
        st.title("Data Cleaning")
        churn.loc[(churn['Total Charges'] == ' '), 'Total Charges'] = 0
        churn['Total Charges'] = pd.to_numeric(churn['Total Charges'])

        numerical = ['Churn Score', 'CLTV','Latitude', 'Longitude','Monthly Charges',
                     'Tenure Months','Total Charges','Zip Code']

        def interactiveplot(dataframe):
            # xval =  st.selectbox("Select X value", options = 'Churn Label')
            yval = st.selectbox("Select variable for box plot ", options=numerical)
            plot = px.box(dataframe, x='Churn Label', y=yval)
            st.plotly_chart(plot)


        interactiveplot(churn)
        code = '''plot = px.box(dataframe, x='Churn Label', y=yval)
                            st.plotly_chart(plot)'''
        st.markdown("**Code:**")
        st.code(code, language='python')

        st.markdown('**Remove unwanted variables**')
        code = '''churn = churn.drop(
        ['CustomerID','Count', 'City','Country' , 'State' , 'Lat Long' ,'Churn Label' ,'Churn Reason' ]
        ,axis = 1
    )'''
        st.markdown("**Code:**")
        st.code(code, language='python')
        st.markdown('**Checking for outliers**')
        st.image("/Users/andrewpullar/Desktop/outliers.png")
        code = '''#Convert Total Charges to numeric
    churn.loc[(churn['Total Charges'] == ' '), 'Total Charges'] = 0 
    churn['Total Charges'] = pd.to_numeric(churn['Total Charges'])'''
        st.markdown("**Code:**")
        st.code(code, language='python')
        st.markdown('**Checking for missing values**')
        st.image("/Users/andrewpullar/Desktop/missing.png")
        code = '''# missing data
        md = churn.isnull().sum()
        missing = pd.concat([md], axis=1, keys=['Missing Data'])
        missing'''
        st.markdown("**Code:**")
        st.code(code, language='python')

        st.markdown('**Fix data imbalance**')
        st.image("/Users/andrewpullar/Desktop/resample.png")
        code = '''#Fix data imbalance
        from imblearn.over_sampling import RandomOverSampler
        fix = RandomOverSampler(random_state=0)
        X, y = fix.fit_resample(X, y)
        ax = sea.countplot(x=y)'''
        st.markdown("**Code:**")
        st.code(code, language='python')
        st.markdown('**Handling categorical variables**')
        code = '''dummies = pd.get_dummies(X, columns=columns_to_convert)
        dummies.head()'''
        st.markdown("**Code:**")
        st.code(code, language='python')


    elif choice == 'Modeling':
        #add_selectbox = st.sidebar.selectbox(
          #  "How would you like to predict?",
            #("CSV", "URL"))
        #if add_selectbox == 'CSV':
            st.title("Predict Customer churn")
            st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5190/5190582.png", width=125)
            st.subheader("Select values for each variable to predict the likelihood the customer will churn.")
            with st.container():
                col1, col2, col3 = st.columns(3)

                with col1:
                    gender = st.radio('Select gender', ['Male', 'Female'])
                    sc = st.radio("Customer is a senior citizen", ('Yes', 'No'))
                    monthly_charges = st.number_input('Monthly charges', min_value=18, max_value=118, value=18)
                    total_charges = st.number_input('Total charges', min_value=0, max_value=8684, value=0)
                    internetservice = st.selectbox(' Customer has internet service:', ['dsl', 'no', 'fiber_optic'])
                    onlinesecurity = st.selectbox(' Customer has online security:', ['yes', 'no', 'no_internet_service'])

                with col2:
                    partner = st.radio("Customer has a partner", ('Yes', 'No'))
                    dependents = st.radio("Customer has dependents ", ('Yes', 'No'))
                    onlinebackup = st.selectbox(' Customer has online backup:', ['yes', 'no', 'no_internet_service'])
                    deviceprotection = st.selectbox(' Customer has device protection:',
                                                    ['yes', 'no', 'no_internet_service'])
                    techsupport = st.selectbox(' Customer has tech support:', ['yes', 'no', 'no_internet_service'])
                    streamingtv = st.selectbox(' Customer has streaming tv:', ['yes', 'no', 'no_internet_service'])

                with col3:
                    phone = st.radio("Phone Service", ('Yes', 'No'))
                    multiplelines = st.radio("Multiple Phone lines", ('Yes', 'No'))

                    tenure = st.number_input('Months with company (0-72 months)',
                                             min_value=0, max_value=72, value=0)
                    streamingmovies = st.selectbox(' Customer has streaming movies:', ['yes', 'no', 'no_internet_service'])
                    contract = st.selectbox(' Customer has a contract:', ['month-to-month', 'one_year', 'two_year'])
                    paperlessbilling = st.selectbox(' Customer has paperless billing:', ['yes', 'no'])


            paymentmethod = st.selectbox('Payment option:',
                                         ['bank_transfer_(automatic)', 'credit_card_(automatic)', 'electronic_check',
                                          'mailed_check'])
            output = ""
            output_prob = ""
            input_dict = {
                "gender": gender,
                "seniorcitizen": sc,
                "partner": partner,
                "dependents": dependents,
                "phoneservice": phone,
                "multiplelines": multiplelines,
                "internetservice": internetservice,
                "onlinesecurity": onlinesecurity,
                "onlinebackup": onlinebackup,
                "deviceprotection": deviceprotection,
                "techsupport": techsupport,
                "streamingtv": streamingtv,
                "streamingmovies": streamingmovies,
                "contract": contract,
                "paperlessbilling": paperlessbilling,
                "paymentmethod": paymentmethod,
                "tenure": tenure,
                "monthlycharges": monthly_charges,
                "totalcharges": total_charges
            }

            if st.button("Predict"):
                X = dv.transform([input_dict])
                y_pred = model.predict_proba(X)[0, 1]
                y_pred = round(y_pred,3)
                churn = y_pred >= 0.5
                output_prob = float(y_pred)
                #prediction = model.predict(X)
                #st.write("Prediction: {}".format(prediction))
                if churn >= 0.5:
                    output = "The customer is likely to churn "
                    st.success('{0}, Risk probability: {1}'.format(output, output_prob))
                else:
                    output = " The customer is likely to stay "
                    st.success('{0}, Risk probability: {1}'.format(output, output_prob))


                @st.cache(allow_output_mutation=True)
                def get_data():
                    return []


                get_data().append({"gender": gender,
                                   "seniorcitizen": sc,
                                   "partner": partner,
                                   "dependents": dependents,
                                   "phoneservice": phone,
                                   "multiplelines": multiplelines,
                                   "internetservice": internetservice,
                                   "onlinesecurity": onlinesecurity,
                                   "onlinebackup": onlinebackup,
                                   "deviceprotection": deviceprotection,
                                   "techsupport": techsupport,
                                   "streamingtv": streamingtv,
                                   "streamingmovies": streamingmovies,
                                   "contract": contract,
                                   "paperlessbilling": paperlessbilling,
                                   "paymentmethod": paymentmethod,
                                   "tenure": tenure,
                                   "monthlycharges": monthly_charges,
                                   "totalcharges": total_charges,
                                   "Prediction": output})
                st.markdown("Previous predictions made:")
                st.write(pd.DataFrame(get_data()))

                @st.cache(allow_output_mutation=True)
                def get_data2():
                    return []



                @st.experimental_memo


                def convert_df(churn):
                    return churn.to_csv(index=False).encode('utf-8')


                csv = convert_df(pd.DataFrame(get_data()))

                st.download_button(
                    "Download predictions",
                    csv,
                    "file.csv",
                    "text/csv",
                    key='download-csv'
                )
                clear = st.button("Clear")
                if clear:
                    st.write(pd.DataFrame(get_data.clear()))


