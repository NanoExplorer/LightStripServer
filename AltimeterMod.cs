using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.Net.Sockets;

using UnityEngine;
using KSP;

using System.IO;

namespace AltimeterMod
{
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class AltimeterMod : KSPPluginFramework.MonoBehaviourExtended
    {
        public IPEndPoint endPoint;
        public Socket mySocket;
        public double lastSent;

        internal override void Awake()
        {
            StreamReader reader = new StreamReader("ip.txt");
            mySocket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
            lastSent = -7520;
            try
            {
                endPoint = new IPEndPoint(IPAddress.Parse(reader.ReadLine()), 12625);

                LogFormatted("Parent is awake");


                //Create a Child Object
                MBExtendedChild Child = gameObject.AddComponent<MBExtendedChild>();

                //Start the repeating worker to fire 10 times each second
                StartRepeatingWorker(10);
            }
            catch
            {
                //fail quietly
                LogFormatted("Could not read ip file.");
            }
            finally
            {
                reader.Close();
            }

        }

        internal override void RepeatingWorker()
        {
            double output;
            if (FlightGlobals.ActiveVessel.situation == Vessel.Situations.LANDED | FlightGlobals.ActiveVessel.situation == Vessel.Situations.PRELAUNCH | FlightGlobals.ActiveVessel.situation == Vessel.Situations.SPLASHED)
            {
                output = 0d;
            }
            else
            {
                double altitude = FlightGlobals.ActiveVessel.altitude;
                double terrainHeight = FlightGlobals.ActiveVessel.terrainAltitude;
                double radarAltitude = altitude - terrainHeight;
                if (radarAltitude < 3000 && terrainHeight > 0)
                {
                    output = radarAltitude;
                }
                else
                {
                    output = altitude;
                }


            }

            if ((output != lastSent && lastSent != 0 && Math.Abs((output - lastSent) / lastSent) > .01) | (lastSent == 0 && Math.Abs(output) > 1))
            {
                string message = "ALT:" + output;
                byte[] sendbuf = Encoding.ASCII.GetBytes(message);
                mySocket.SendTo(sendbuf, endPoint);
                lastSent = output;
            }


          
            
            //LogFormatted("Last RepeatFunction Ran for: {0}ms", RepeatingWorkerDuration.TotalMilliseconds);
            //LogFormatted("UT Since Last RepeatFunction: {0}", RepeatingWorkerUTPeriod);
        }
    }

    public class MBExtendedChild : KSPPluginFramework.MonoBehaviourExtended
    {
        internal override void Awake()
        {
            //LogFormatted("Child is awake");
        }
    }
}
