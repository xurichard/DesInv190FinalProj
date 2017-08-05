//
//  ViewController.swift
//  Arduino_Servo
//
//  Created by Owen L Brown on 9/24/14.
//  Copyright (c) 2014 Razeware LLC. All rights reserved.
//

import UIKit

class ViewController: UIViewController, UITextFieldDelegate {
  
  @IBOutlet weak var imgBluetoothStatus: UIImageView!
  @IBOutlet weak var dosageAlarmToggle: UISegmentedControl!
  @IBOutlet weak var alarmField: UITextField!
  @IBOutlet weak var buddyNumber: UITextField!
  
  var lastBuddyNumber = "1234567890"
  var dosageNum = 0
  var timerTXDelay: Timer?
  var allowTX = true
  var lastAlarmTimeArr: [String] = ["12:00", "12:00", "12:00"]
  var alarmTimeArr: [String] = ["12:00", "12:00", "12:00"]
  var datePicker : UIDatePicker!
  
  override func viewDidLoad() {
    super.viewDidLoad()
    alarmField.delegate = self
    buddyNumber.delegate = self
    // Do any additional setup after loading the view, typically from a nib.
    
    // keyboard init
    
    NotificationCenter.default.addObserver(self, selector: #selector(ViewController.keyboardWillShow(sender:)), name:NSNotification.Name.UIKeyboardWillShow, object: nil)
    NotificationCenter.default.addObserver(self, selector: #selector(ViewController.keyboardWillHide(sender:)), name:NSNotification.Name.UIKeyboardWillHide, object: nil)
    
    // Watch Bluetooth connection
    NotificationCenter.default.addObserver(self, selector: #selector(ViewController.connectionChanged(_:)), name: NSNotification.Name(rawValue: BLEServiceChangedStatusNotification), object: nil)
    
    // Start the Bluetooth discovery process
    _ = btDiscoverySharedInstance
  }
  override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    // Dispose of any resources that can be recreated.
  }
    
  func keyboardWillShow(sender: NSNotification) {
    self.view.frame.origin.y = -150 // Move view 150 points upward
  }
    
  func keyboardWillHide(sender: NSNotification) {
    self.view.frame.origin.y = 0 // Move view to original position
  }
    
  
  //MARK:- alarmField Delegate
  func textFieldDidBeginEditing(_ textField: UITextField) {
    self.pickUpDate(self.alarmField)
  }
    
  //MARK:- Function of datePicker
  func pickUpDate(_ textField : UITextField){
        
    // DatePicker
    self.datePicker = UIDatePicker(frame:CGRect(x: 0, y: 0, width: self.view.frame.size.width, height: 216))
    self.datePicker.backgroundColor = UIColor.white
    self.datePicker.datePickerMode = UIDatePickerMode.time
    textField.inputView = self.datePicker
        
    // ToolBar
    let toolBar = UIToolbar()
    toolBar.barStyle = .default
    toolBar.isTranslucent = true
    toolBar.tintColor = UIColor(red: 92/255, green: 216/255, blue: 255/255, alpha: 1)
    toolBar.sizeToFit()
    
    // Adding Button ToolBar
    let doneButton = UIBarButtonItem(title: "Done", style: .plain, target: self, action: #selector(ViewController.doneClick))
    let spaceButton = UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil)
    let cancelButton = UIBarButtonItem(title: "Cancel", style: .plain, target: self, action: #selector(ViewController.cancelClick))
    toolBar.setItems([cancelButton, spaceButton, doneButton], animated: false)
    toolBar.isUserInteractionEnabled = true
    textField.inputAccessoryView = toolBar
        
  }
    
  // MARK:- Button Done and Cancel
  func doneClick() {
    let dateFormatter1 = DateFormatter()
    dateFormatter1.dateStyle = .none
    dateFormatter1.timeStyle = .short
    alarmTimeArr[dosageNum] = dateFormatter1.string(from: datePicker.date)
    alarmField.text = alarmTimeArr[dosageNum]
    alarmField.resignFirstResponder()
  }
  func cancelClick() {
    alarmField.resignFirstResponder()
  }
    
 // ---------------------------------
    
  //Mark:- buddyNumber Delegate
  func textFieldDidEndEditing(_ textField: UITextField) {
    self.finishEditNumber(self.buddyNumber)
  }
  
  //Mark:- Function for ToolBar of buddyNumber input 
  func finishEditNumber(_ textField : UITextField) {
    // BuddyToolBar
    let buddyToolBar = UIToolbar()
    buddyToolBar.barStyle = .default
    buddyToolBar.isTranslucent = true
    buddyToolBar.tintColor = UIColor(red: 92/255, green: 216/255, blue: 255/255, alpha: 1)
    buddyToolBar.sizeToFit()
    
    // Adding Button BuddyToolBar
    let doneButton = UIBarButtonItem(title: "Done", style: .plain, target: self, action: #selector(ViewController.buddyDoneClick))
    let spaceButton = UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil)
    buddyToolBar.setItems([spaceButton, doneButton], animated: false)
    buddyToolBar.isUserInteractionEnabled = true
    textField.inputAccessoryView = buddyToolBar
  }
  
  // Mark:- Button done and Cancel for BuddyToolBar
  func buddyDoneClick() {
    buddyNumber.resignFirstResponder()
  }
    
    

  deinit {
    NotificationCenter.default.removeObserver(self, name: NSNotification.Name(rawValue: BLEServiceChangedStatusNotification), object: nil)
  }
  
  override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    
    self.stopTimerTXDelay()
  }
  
  @IBAction func dosageToggleChanged(_ sender: UISegmentedControl)
  {
    print("yo in here")
    dosageNum = sender.selectedSegmentIndex
    alarmField.text = alarmTimeArr[dosageNum]
  }

    
  func connectionChanged(_ notification: Notification) {
    // Connection status changed. Indicate on GUI.
    let userInfo = (notification as NSNotification).userInfo as! [String: Bool]
    
    DispatchQueue.main.async(execute: {
      // Set image based on connection status
      if let isConnected: Bool = userInfo["isConnected"] {
        if isConnected {
          self.imgBluetoothStatus.image = UIImage(named: "Bluetooth_Connected")

        } else {
          self.imgBluetoothStatus.image = UIImage(named: "Bluetooth_Disconnected")
        }
      }
    });
  }

  
  func sendValues(_ alarms: [String]) {

    if !allowTX {
      return
    }
    
    // Validate values
    // Phone #
    let currentBuddyNum = buddyNumber.text
    // Alarms
    var changed = 0
    for i in 0..<3 {
      if alarms[i] != lastAlarmTimeArr[i] {
        changed += 1
      }
    }
    if changed == 0 && currentBuddyNum != lastBuddyNumber {
      return
    }
    
    // Send alarms to BLE Shield (if service exists and is connected)
    if let bleService = btDiscoverySharedInstance.bleService {
      let values : [String] = [alarms[0], alarms[1], alarms[2], currentBuddyNum!]
      bleService.writeValues(values)
      // copying over updated values
      for i in 0..<3 {
        lastAlarmTimeArr[i] = alarms[i]
      }
      lastBuddyNumber = values[3]
      // Start delay timer
      allowTX = false
      if timerTXDelay == nil {
        timerTXDelay = Timer.scheduledTimer(timeInterval: 0.1, target: self, selector: #selector(ViewController.timerTXDelayElapsed), userInfo: nil, repeats: false)
      }
    }
  }
  
  func timerTXDelayElapsed() {
    self.allowTX = true
    self.stopTimerTXDelay()
    
    // Send current slider position
    self.sendValues(self.alarmTimeArr)
  }
  
  func stopTimerTXDelay() {
    if self.timerTXDelay == nil {
      return
    }
    
    timerTXDelay?.invalidate()
    self.timerTXDelay = nil
  }
  
}

